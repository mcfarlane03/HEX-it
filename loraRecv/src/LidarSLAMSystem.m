classdef LidarSLAMSystem < handle
    properties
        % Hardware Interface
        serialPort
        
        % SLAM Components
        maxRange = 20;          % meters
        minRange = 0.1;         % meters
        slamAlgo
        optimizedPoses
        map
        
        % Visualization
        fig
        scanAxes
        mapAxes
        infoText
    end
    
    methods
        function obj = LidarSLAMSystem(port)
            % Initialize serial connection
            obj.serialPort = serialport(port, 115200);
            configureTerminator(obj.serialPort, "LF");
            
            % Wait for device ready signal
            disp('Waiting for device...');
            % while true
            %     line = readline(obj.serialPort);
            %     if contains(line, "MATLAB_READY")
            %         break;
            %     end
            % end
            disp('Device ready!');
            
            % Initialize SLAM (updated for current MATLAB versions)

            obj.slamAlgo = lidarSLAM(10,obj.maxRange);
            obj.slamAlgo.LoopClosureThreshold = 360;
            obj.slamAlgo.LoopClosureSearchRadius = 8;
            
            % Initialize map
            obj.map = occupancyMap(40, 40, 20); % 40x40m at 20 cells/meter
            
            % Setup visualization
            obj.setupFigure();
        end
        
        function setupFigure(obj)
            obj.fig = figure('Name', '2D LIDAR SLAM', 'Position', [100 100 1200 600]);
            
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
            
            % Info panel
            obj.infoText = uicontrol('Style', 'text', ...
                'Position', [800 50 350 500], ...
                'FontSize', 10, ...
                'HorizontalAlignment', 'left');
        end
        
        function run(obj)
            % Main processing loop
            while ishandle(obj.fig)
                if obj.serialPort.NumBytesAvailable > 0
                    line = readline(obj.serialPort);
                    obj.processScan(line);
                end
                pause(0.01);
            end
        end
        
        function processScan(obj, jsonStr)
            try
                data = jsondecode(jsonStr);
                
                if isfield(data, 'ranges')
                    % Convert and filter data
                    ranges = double(data.ranges)/100; % cm→m
                    angles = deg2rad(double(data.angles));
                    
                    valid = (ranges >= obj.minRange) & (ranges <= obj.maxRange);
                    scan  = lidarScan(ranges(valid), angles(valid));
                    
                    % figure;
                    % plot(scan);

                    % Add scan to SLAM (updated property access)
                    isAccepted = addScan(obj.slamAlgo, scan);
                    
                    if isAccepted
                        % Update map using poseGraph (new property name)
                        [scans, obj.optimizedPoses] = scansAndPoses(obj.slamAlgo);
                        
                        % Only update recent scans for performance
                        for i = max(1, length(scans)-3):length(scans)
                            insertRay(obj.map, obj.optimizedPoses(i,:), scans{i}, obj.maxRange);
                        end
                        
                        % Visualize
                        obj.updateDisplay(scan)
                    end
                end
            catch ME
                disp(['Error: ' ME.message]);
            end
        end
        
        function updateDisplay(obj, scan)
            % Current scan
            cla(obj.scanAxes);
            plot(scan, 'Parent', obj.scanAxes);
            title(obj.scanAxes, sprintf('Scan: %d points', scan.Count));
            
            % Occupancy map
            cla(obj.mapAxes);
            show(obj.map, 'Parent', obj.mapAxes);
            hold(obj.mapAxes, 'on');
            if ~isempty(obj.optimizedPoses)
                plot(obj.mapAxes, obj.optimizedPoses(:,1), obj.optimizedPoses(:,2), 'r-', 'LineWidth', 2);
            end
            hold(obj.mapAxes, 'off');
            
            % Info panel (updated with current property names)
            infoStr = sprintf([...
                'SLAM Status:\n' ...
                'Scans: %d\n' ...
                'Loop Closures: %d\n' ...
                'Map Size: %.1f x %.1f m\n' ...
                'Trajectory: %.1f m'], ...
                length(scans), ...
                obj.slamAlgo.LoopClosureCount, ...
                obj.map.XWorldLimits(2), ...
                obj.map.YWorldLimits(2), ...
                sum(sqrt(sum(diff(obj.optimizedPoses).^2, 2))));
            set(obj.infoText, 'String', infoStr);
            
            drawnow;
        end
        
        function saveResults(obj)
            % Save final results (updated property names)
            results = struct(...
                'map', obj.map, ...
                'poses', obj.optimizedPoses, ...
                'scans', {scans}, ...  % Cell array of scans
                'poseGraph', poseGraph);
            
            save('slam_results.mat', 'results');
            
            % Export visualization
            figure;
            show(obj.map);
            hold on;
            plot(obj.optimizedPoses(:,1), obj.optimizedPoses(:,2), 'r-', 'LineWidth', 2);
            saveas(gcf, 'slam_map.png');
        end
    end
end