classdef LidarVisualization < handle
    properties
        serialPort
        baudRate = 115200;
        portName = 'COM3'; % Change this to your actual COM port
        timeout = 10;
        
        % Visualization properties
        figureHandle
        axesHandle
        scanHandle
        mapHandle
        
        % Mapping properties
        maxLidarRange = 4000; % mm (adjust based on your sensor)
        mapResolution = 20; % cells per meter
        mapWidth = 20; % meters
        mapHeight = 20; % meters
        occupancyMap
    end
    
    methods
        function obj = LidarVisualization()
            % Initialize the visualization
            obj.initializeVisualization();
            
            % Set up serial connection
            try
                obj.serialPort = serialport(obj.portName, obj.baudRate, 'Timeout', obj.timeout);
                configureTerminator(obj.serialPort, "LF");
                disp(['Connected to serial port: ' obj.portName]);
                
                % Start reading data
                obj.readSerialData();
            catch ME
                disp(['Error opening serial port: ' ME.message]);
                delete(obj);
            end
        end
        
        function initializeVisualization(obj)
            % Create figure and axes
            obj.figureHandle = figure('Name', 'LiDAR Visualization', 'NumberTitle', 'off');
            obj.axesHandle = axes('Parent', obj.figureHandle);
            
            % Initialize occupancy map
            obj.occupancyMap = occupancyMap(obj.mapWidth, obj.mapHeight, obj.mapResolution);
            obj.occupancyMap.FreeThreshold = 0.2;
            obj.occupancyMap.OccupiedThreshold = 0.7;
            
            % Create visualization handles
            hold(obj.axesHandle, 'on');
            obj.scanHandle = plot(obj.axesHandle, 0, 0, 'b.'); % For current scan
            obj.mapHandle = show(obj.occupancyMap, 'Parent', obj.axesHandle);
            hold(obj.axesHandle, 'off');
            
            title(obj.axesHandle, 'LiDAR Scan and Occupancy Map');
            xlabel(obj.axesHandle, 'X (mm)');
            ylabel(obj.axesHandle, 'Y (mm)');
            axis(obj.axesHandle, 'equal');
            grid(obj.axesHandle, 'on');
        end
        
        function readSerialData(obj)
            while ishandle(obj.figureHandle)
                % Check for available data
                if obj.serialPort.NumBytesAvailable > 0
                    try
                        % Read a line of JSON data
                        jsonStr = readline(obj.serialPort);
                        
                        % Parse JSON
                        data = jsondecode(jsonStr);
                        
                        % Extract ranges and angles (convert to meters and radians)
                        ranges = double(data.ranges) / 1000; % mm to m
                        angles = deg2rad(double(data.angles)); % degrees to radians
                        
                        % Create lidarScan object
                        scan = lidarScan(ranges, angles);
                        
                        % Update visualization
                        obj.updateVisualization(scan);
                        
                        % Update occupancy map
                        obj.updateOccupancyMap(scan);
                    catch ME
                        disp(['Error processing data: ' ME.message]);
                        continue;
                    end
                end
                
                % Small pause to prevent CPU overload
                pause(0.01);
            end
            
            % Clean up when figure is closed
            obj.cleanup();
        end
        
        function updateVisualization(obj, scan)
            % Convert to cartesian coordinates for plotting
            cart = scan.Cartesian;
            
            % Update current scan plot
            set(obj.scanHandle, 'XData', cart(:,1)*1000, 'YData', cart(:,2)*1000);
            
            % Refresh display
            drawnow limitrate;
        end
        
        function updateOccupancyMap(obj, scan)
            % Insert scan into occupancy map
            pose = [0 0 0]; % Assuming robot is at origin (adjust if you have odometry)
            insertRay(obj.occupancyMap, pose, scan, obj.maxLidarRange);
            
            % Update map visualization every N scans to improve performance
            persistent scanCount;
            if isempty(scanCount)
                scanCount = 0;
            end
            
            scanCount = scanCount + 1;
            if mod(scanCount, 5) == 0
                set(obj.mapHandle, 'CData', obj.occupancyMap.occupancyMatrix);
                drawnow limitrate;
            end
        end
        
        function cleanup(obj)
            % Clean up serial connection
            if ~isempty(obj.serialPort) && isvalid(obj.serialPort)
                delete(obj.serialPort);
                disp('Serial port closed.');
            end
        end
        
        function delete(obj)
            % Destructor
            obj.cleanup();
        end
    end
end