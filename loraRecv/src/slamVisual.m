% LoRa SLAM in MATLAB with IMU-based Odometry
clear;
clc;

% Serial Port Configuration
serialPort = 'COM3';   % Change this to your Arduino's serial port
baudRate = 115200;
s = serialport(serialPort, baudRate);

% SLAM Parameters
maxRange = 10;       % Maximum range of the sensor (meters)
mapResolution = 20;  % Cells per meter
slamAlg = lidarSLAM(mapResolution, maxRange);

% Odometry Parameters
pose = [0, 0, 0];  % Initial pose [x, y, theta]
lastTime = tic;    % Timer for delta time calculation

% Loop to Continuously Receive Data and Update Map
disp('Starting SLAM...');
while true
    try
        % Read JSON data from serial port
        data = readline(s);
        jsonData = jsondecode(data);
        
        % Extract Lidar data
        ranges = double(jsonData.ranges) / 100; % Convert cm to meters
        angles = double(jsonData.angles) * pi / 180; % Convert degrees to radians
        
        % Create Lidar scan
        scan = lidarScan(ranges, angles);
        
        % Extract IMU data
        gyroZ = double(jsonData.rotation_z);
        accelX = double(jsonData.accel_x);
        accelY = double(jsonData.accel_y);
        
        % Calculate delta time
        currentTime = toc(lastTime);
        lastTime = tic;
        
        % Estimate velocity from accelerometer data (integrate acceleration)
        vX = accelX * currentTime;
        vY = accelY * currentTime;
        
        % Convert to robot-centric velocities
        v = sqrt(vX^2 + vY^2);    % Approximate forward velocity
        omega = gyroZ;            % Rotational velocity from gyro
        
        % Update pose using a simple motion model
        deltaTheta = omega * currentTime;
        pose(3) = pose(3) + deltaTheta;
        
        % Handle theta overflow
        pose(3) = wrapToPi(pose(3));
        
        % Calculate displacement in robot frame
        dx = v * cos(pose(3)) * currentTime;
        dy = v * sin(pose(3)) * currentTime;
        
        % Update pose (x, y) using odometry
        pose(1) = pose(1) + dx;
        pose(2) = pose(2) + dy;
        
        % Use pose for SLAM prediction
        [isScanAccepted, loopClosureInfo, slamPose] = addScan(slamAlg, scan, pose);
        
        % Update the SLAM map if the scan is accepted
        if isScanAccepted
            fprintf('Scan accepted. SLAM Position: (%.2f, %.2f, %.2f)\n', slamPose(1), slamPose(2), slamPose(3));
            
            % Display updated map
            figure(1);
            show(slamAlg);
            title('Real-time SLAM Map with IMU Odometry');
            drawnow;
        else
            disp('Scan rejected.');
        end
        
    catch ME
        disp(['Error: ', ME.message]);
    end
end

% Cleanup
clear s;
disp('SLAM process terminated.');
