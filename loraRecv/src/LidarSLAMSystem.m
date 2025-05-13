classdef LidarSLAMSystem < handle
    properties
        % Hardware Interface
        serialPort
        
        % SLAM Components
        maxRange = 8;          % meters
        minRange = 0.1;        % meters
        slamAlgo
        optimizedPoses
        map
        scans
        poseGraph
        
        % IMU Integration
        lastImuTime = 0
        imuYaw = 0
        imuPosition = [0 0]
        imuVelocity = [0 0]
        imuAccel = [0 0]
        
        % Event Markers
        temperatureEvents = []
        personEvents = []
        
        % Visualization
        fig
        scanAxes
        mapAxes
        infoText
        imuText
    end
    
    methods
        function obj = LidarSLAMSystem(port)
            % Initialize serial connection
            obj.serialPort = serialport(port, 115200);
            configureTerminator(obj.serialPort, "LF");
            disp('Device ready!');
            
            % Initialize SLAM with tighter parameters for IMU fusion
            obj.slamAlgo = lidarSLAM(20, obj.maxRange); % More frequent updates
            obj.slamAlgo.LoopClosureThreshold = 360;
            obj.slamAlgo.LoopClosureSearchRadius = 8;
            
            % Initialize larger map centered at origin
            obj.map = occupancyMap(20, 20, 20);
            obj.map.LocalOriginInWorld = [-20 -20]; % Center the map
            
            % Setup visualization
            obj.setupFigure();
            
            % Prime the map display to prevent initial rendering issues
            figure('Visible', 'off');
            show(obj.map);
            close;
        end
        
        function setupFigure(obj)
            obj.fig = figure('Name', 'LIDAR+IMU SLAM', 'Position', [100 100 1200 600]);
            
            % Scan plot
            obj.scanAxes = subplot(1,2,1);
            title('Current Scan');
            axis equal;
            grid on;
            xlim([-obj.maxRange obj.maxRange]);
            ylim([-obj.maxRange obj.maxRange]);
            
            % Map plot
            obj.mapAxes = subplot(1,2,2);
            title('Occupancy Map');
            axis equal;
        end
        
        function run(obj)
            % Main processing loop
            while ishandle(obj.fig)
                if obj.serialPort.NumBytesAvailable > 0
                    line = readline(obj.serialPort);
                    obj.processData(line);
                end
                pause(0.01);
            end
        end
        
        function processData(obj, jsonStr)
            try
                data = jsondecode(jsonStr);
                
                if isfield(data, 'ranges')
                    obj.processLidarScan(data);
                end
                
                if isfield(data, 'imu')
                    obj.processImuData(data.imu);
                end
                
                % Process temperature data if available
                if isfield(data, 'temperature')
                    obj.processTemperature(data.temperature);
                end
                
                % Process person detection if available
                if isfield(data, 'personDetectedFlag')  % Note: Fixed typo from original
                    obj.processPersonDetection(data.personDetectedFlag);
                end
                
            catch ME
                disp(['Error: ' ME.message]);
            end
        end
        
        function processTemperature(obj, temp)
            % Record high temperature events
            if temp > 34
                if ~isempty(obj.optimizedPoses)
                    currentPose = obj.optimizedPoses(end,:);
                    obj.temperatureEvents = [obj.temperatureEvents; currentPose];
                    disp(['High temperature detected: ' num2str(temp) '°C']);
                end
            end
        end
        
        function processPersonDetection(obj, detected)
            % Record person detection events
            if detected && ~isempty(obj.optimizedPoses)
                currentPose = obj.optimizedPoses(end,:);
                obj.personEvents = [obj.personEvents; currentPose];
                disp('Person detected!');
            end
        end
        
        function processImuData(obj, imuData)
            % Calculate time delta in seconds
            currentTime = imuData.timestamp / 1e6; % Convert μs to s
            if obj.lastImuTime == 0
                dt = 0;
            else
                dt = currentTime - obj.lastImuTime;
            end
            obj.lastImuTime = currentTime;
            
            % Update orientation (integrate gyroZ)
            obj.imuYaw = obj.imuYaw + imuData.gyroZ * dt;
            
            % Update velocity (integrate acceleration)
            rotation = [cos(obj.imuYaw) -sin(obj.imuYaw); 
                       sin(obj.imuYaw)  cos(obj.imuYaw)];
            worldAccel = rotation * [imuData.accelX; imuData.accelY];
            
            obj.imuVelocity = obj.imuVelocity + worldAccel' * dt;
            
            % Update position (integrate velocity)
            obj.imuPosition = obj.imuPosition + obj.imuVelocity * dt;
            
            % Store current acceleration
            obj.imuAccel = [imuData.accelX, imuData.accelY];
        end
        
        function processLidarScan(obj, data)
            % Convert and filter LIDAR data
            ranges = double(data.ranges)/100; % cm→m
            angles = deg2rad(double(data.angles));
            valid = (ranges >= obj.minRange) & (ranges <= obj.maxRange);
            scan = lidarScan(ranges(valid), angles(valid));
            
            % Create motion prediction from IMU
            if obj.lastImuTime > 0
                predictedPose = [obj.imuPosition, obj.imuYaw];
            else
                predictedPose = [0 0 0]; % Default if no IMU data
            end
            
            % Add scan to SLAM with IMU prediction
            [isAccepted, ~, obj.optimizedPoses] = addScan(obj.slamAlgo, scan, predictedPose);
            
            if isAccepted
                % Update SLAM state
                [obj.scans, obj.optimizedPoses] = scansAndPoses(obj.slamAlgo);
                obj.poseGraph = obj.slamAlgo.PoseGraph;
                
                % Update map with ALL scans - fixed to update complete map
                obj.map = occupancyMap(40, 40, 20); % Reset the map
                obj.map.LocalOriginInWorld = [-20 -20]; % Center the map
                
                % Insert all scans at their optimized poses
                for i = 1:length(obj.scans)
                    insertRay(obj.map, obj.optimizedPoses(i,:), obj.scans{i}, obj.maxRange);
                end
                
                % Correct IMU estimate with SLAM output
                if ~isempty(obj.optimizedPoses)
                    slamPose = obj.optimizedPoses(end,:);
                    obj.imuPosition = slamPose(1:2);
                    obj.imuYaw = slamPose(3);
                end
                
                obj.updateDisplay(scan);
            end
        end
        
        function updateDisplay(obj, scan)
            % Current scan
            cla(obj.scanAxes);
            plot(scan, 'Parent', obj.scanAxes);
            title(obj.scanAxes, sprintf('Scan: %d points', scan.Count));
            
            % Occupancy map - using different approach to fix clipping
            cla(obj.mapAxes);
            
            % First create a figure handle to properly build the map
            mapFig = figure('Visible', 'off');
            show(obj.map);
            mapAxImg = getframe(gca);
            close(mapFig);
            
            % Now display the captured image in our axes
            image(obj.mapAxes, mapAxImg.cdata);
            
            % Reset the axes to match map coordinates
            ax = obj.mapAxes;
            ax.YDir = 'normal';  % Fix orientation
            
            % Set axes to match map world coordinates
            mapWidth = obj.map.XWorldLimits(2) - obj.map.XWorldLimits(1);
            mapHeight = obj.map.YWorldLimits(2) - obj.map.YWorldLimits(1);
            
            % Set proper axis limits and scale
            axis(ax, [1 size(mapAxImg.cdata, 2) 1 size(mapAxImg.cdata, 1)]);
            
            % Convert from image coordinates to world coordinates for plotting
            xScale = size(mapAxImg.cdata, 2) / mapWidth;
            yScale = size(mapAxImg.cdata, 1) / mapHeight;
            
            % Define matrix to transform world coordinates to image coordinates
            xOffset = -obj.map.XWorldLimits(1) * xScale;
            yOffset = -obj.map.YWorldLimits(1) * yScale;
            
            hold(obj.mapAxes, 'on');
            
            % Plot trajectory in image coordinates
            if ~isempty(obj.optimizedPoses)
                % Convert world coordinates to image coordinates
                xWorld = obj.optimizedPoses(:,1);
                yWorld = obj.optimizedPoses(:,2);
                
                xImg = xWorld * xScale + xOffset;
                yImg = yWorld * yScale + yOffset;
                
                plot(obj.mapAxes, xImg, yImg, 'r-', 'LineWidth', 2);
                
                % Plot current position marker
                currentPose = obj.optimizedPoses(end,:);
                currX = currentPose(1) * xScale + xOffset;
                currY = currentPose(2) * yScale + yOffset;
                plot(obj.mapAxes, currX, currY, 'ro', 'MarkerSize', 6, 'MarkerFaceColor', 'r');
            end
            
            % Plot temperature events (blue stars)
            if ~isempty(obj.temperatureEvents)
                tempX = obj.temperatureEvents(:,1) * xScale + xOffset;
                tempY = obj.temperatureEvents(:,2) * yScale + yOffset;
                plot(obj.mapAxes, tempX, tempY, 'rx', 'MarkerSize', 8, 'LineWidth', 1.5);
            end
            
            % Plot person detection events (green diamonds)
            if ~isempty(obj.personEvents)
                personX = obj.personEvents(:,1) * xScale + xOffset;
                personY = obj.personEvents(:,2) * yScale + yOffset;
                plot(obj.mapAxes, personX, personY, 'go', 'MarkerSize', 8, 'LineWidth', 1.5);
            end
            
            % Add legend if we have any events
            if ~isempty(obj.temperatureEvents) || ~isempty(obj.personEvents)
                legendEntries = {};
                if ~isempty(obj.temperatureEvents)
                    legendEntries{end+1} = 'High Temp';
                end
                if ~isempty(obj.personEvents)
                    legendEntries{end+1} = 'Person';
                end
                legend(obj.mapAxes, legendEntries, 'Location', 'northeast');
            end
            
            hold(obj.mapAxes, 'off');
        end
        
        function saveResults(obj)
            results = struct(...
                'map', obj.map, ...
                'poses', obj.optimizedPoses, ...
                'scans', {obj.scans}, ...
                'poseGraph', obj.poseGraph, ...
                'temperatureEvents', obj.temperatureEvents, ...
                'personEvents', obj.personEvents);
            
            save('slam_results.mat', 'results');
            
            figure;
            show(obj.map);
            hold on;
            
            % Plot events on saved map
            if ~isempty(obj.temperatureEvents)
                plot(obj.temperatureEvents(:,1), obj.temperatureEvents(:,2), 'b*', 'MarkerSize', 8, 'LineWidth', 1.5);
            end
            if ~isempty(obj.personEvents)
                plot(obj.personEvents(:,1), obj.personEvents(:,2), 'gd', 'MarkerSize', 8, 'LineWidth', 1.5);
            end
            
            % Add legend if needed
            if ~isempty(obj.temperatureEvents) || ~isempty(obj.personEvents)
                legendEntries = {};
                if ~isempty(obj.temperatureEvents)
                    legendEntries{end+1} = 'High Temp';
                end
                if ~isempty(obj.personEvents)
                    legendEntries{end+1} = 'Person';
                end
                legend(legendEntries);
            end
            
            saveas(gcf, 'slam_map.png');
        end
    end
end