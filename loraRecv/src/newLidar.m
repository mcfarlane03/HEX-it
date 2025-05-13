% newLidar.m
% This script reads data from the serial monitor and decodes JSON messages.

% Configure the serial port
serialPort = "COM3"; % Replace with your serial port
baudRate = 115200; % Set the baud rate
s = serialport(serialPort, baudRate);


% Set up LiDAR scan map
% Define the parameters for the LiDAR scan map
maxRange = 8; % Maximum range in meters
minRange = 0; % Minimum range in meters
gridResolution = 20; % Grid resolution in meters
mapObj = lidarscanmap(gridResolution, maxRange);

% Set a timeout for reading
configureTerminator(s, "LF");
flush(s);

disp("Listening to serial port...");

while true
    try
        % Read a line of data from the serial port
        if s.NumBytesAvailable > 0
            data = readline(s);
            
            % Decode the JSON data
            jsonData = jsondecode(data);

            % Display the decoded JSON data
            ranges = double(data.ranges)/100; % cm→m
            angles = deg2rad(double(data.angles));

            valid = (ranges >= minRange) & (ranges <= maxRange);
            scan = lidarScan(ranges(valid), angles(valid));

            person_detected = jsonData.personDetectedFlag;
            temperature = jsonData.temperature;
            
            isAccepted = addScan(mapObj, scan);
            if isAccepted
                % Update the map with the new scan
                disp("Scan added to the map.");
            else
                disp("Scan rejected.");
            end
        end
    catch ME
        % Handle errors (e.g., invalid JSON or serial issues)
        disp("Error reading or decoding data:");
        disp(ME.message);
    end
    pause(0.1); % Small delay to prevent CPU overuse
end

% Cleanup
clear s; % Close the serial port when done