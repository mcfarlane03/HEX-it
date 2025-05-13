% main_pathfinder.m
% Load a blueprint and find a path avoiding fire zones toward detected people.

clear; clc; close all;

%% STEP 1: Load and preprocess the blueprint image
img = imread('testerplan.png');        % Replace with your blueprint file
gray = rgb2gray(img);                 % Convert to grayscale
bw = imcomplement(imbinarize(rgb2gray(img))); % Convert to binary (adjust as needed)

M = bw;                               % M is the obstacle map: 1 = blocked, 0 = free               
% imshow(M); title('Initial Map (WhitFe = Free, Black = Obstacle)');

%% STEP 2: Add fire zone coordinates (example points)
% Replace with your real fire detection output
num_fires = 5;
fire_coords = [];
fire_affected_zones = []; % Track all cells affected by fire zones

for i = 1:num_fires
    placed = false;
    while ~placed
        row = randi(size(M,1));
        col = randi(size(M,2));
        if M(row, col) == 0  % Only place fire on free space
            fire_coords(end+1, :) = [row, col];
            
            % Mark fire + 8-neighbors (3x3 area) as obstacle in M and track in fire_affected_zones
            for dr = -1:1
                for dc = -1:1
                    r2 = row + dr;
                    c2 = col + dc;
                    if r2 > 0 && r2 <= size(M,1) && c2 > 0 && c2 <= size(M,2)
                        M(r2, c2) = 1; % Mark as obstacle
                        fire_affected_zones(end+1, :) = [r2, c2]; % Track this affected cell
                    end
                end
            end
            placed = true;
        end
    end
end


%% STEP 3: Simulate a Person on the Map
% Let's assume the person's position is detected at a certain point
person_row = 100;  % Example row of the person's position
person_col = 140;  % Example column of the person's position

% Mark the person's position for visualization (but not as an obstacle)
M(person_row, person_col) = 0;

%% STEP 4: Display initial map with fires and person
fig1 = figure;
imshow(~M); hold on;


% Plot fire centers with 'x' markers

radii = 1.5 * sqrt(2); % Circle to cover 3x3 area roughly
h_circles = viscircles(fire_coords(:, [2 1]), repmat(radii, size(fire_coords,1), 1), ...
           'Color', 'r', 'LineStyle', 'none', 'LineWidth', 1);


h_fire = plot(fire_coords(:,2), fire_coords(:,1), 'rx', 'MarkerSize', 8, 'LineWidth', 2);
% Plot person
h_person = plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
title('Map with Fire Zones and Person (Click START Point)');

 legend([h_fire, h_circles, h_person], {'Fire Centers', 'Fire Region ','Person'}, ...
        'Location','southoutside','Orientation','horizontal');

%% STEP 5: Define start and end points
valid = false;
while ~valid
    % fig2 = figure;
    % if exist('fig1', 'var') && ishandle(fig1)
    %     close(fig1);
    % end
    imshow(~M); hold on;
    

    status_text = text(10, size(M,1)+10, '', 'Color', 'white', 'FontSize', 12, 'FontWeight', 'bold');

    % Visualize ALL fire-affected zones (both fire points and their surroundings)
    fire_zone_rows = fire_affected_zones(:,1);
    fire_zone_cols = fire_affected_zones(:,2);
    
    
    % Plot fire centers with 'x' markers
    h_fires =plot(fire_coords(:,2), fire_coords(:,1), 'rx', 'MarkerSize', 8, 'LineWidth', 2);
    
    h_circles =plot(fire_zone_cols, fire_zone_rows, 'ro', 'MarkerSize', 4);
    % Plot person
    h_person =plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
    title('Click START point (white = free)');

    legend([h_fire, h_circles, h_person],{'Fire Centers', 'Fire Region ','Person'}, ...
        'Location','southoutside','Orientation','horizontal');

    [c_start, r_start] = ginput(1);
    ri = round(r_start); ci = round(c_start);

     if ri > 0 && ri <= size(M,1) && ci > 0 && ci <= size(M,2)
        is_in_fire_zone = any(ismember(fire_affected_zones, [ri ci], 'rows'));
        if M(ri, ci) == 0 && ~is_in_fire_zone
            valid = true;
            disp(['✅ Start selected at (' num2str(ri) ',' num2str(ci) ')']);
            set(status_text, 'String', 'Start Selected', 'Color', 'green');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        else
            disp('❌ Invalid START! Must be free and not in fire zone.');
            set(status_text, 'String','❌ Invalid START! Must be free and not in fire zone.', 'Color', 'magenta');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        end
    end
end

valid = false;
status_text = text(10, size(M,1)+10, '', 'Color', 'white', 'FontSize', 12, 'FontWeight', 'bold');
while ~valid
    title('Click GOAL point (white = free)');
    [c_end, r_end] = ginput(1);
    rf = round(r_end); cf = round(c_end);

    if rf > 0 && rf <= size(M,1) && cf > 0 && cf <= size(M,2)
        is_in_fire_zone = any(ismember(fire_affected_zones, [rf cf], 'rows'));
        if M(rf, cf) == 0 && ~is_in_fire_zone
            valid = true;
            disp(['✅ Goal selected at (' num2str(rf) ',' num2str(cf) ')']);
            set(status_text, 'String', 'Goal Selected', 'Color', 'magenta');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        else
            disp('❌ Invalid GOAL! Must be free and not in fire zone.');
            set(status_text, 'String', '❌ Invalid GOAL! Must be free and not in fire zone.', 'magenta');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        end
    end
end

%% STEP 6: Call your shpath function
% Run shortest path algorithm
try
    [r, c, H] = shpath(M, ri, ci, rf, cf);  % Your custom pathfinding function
catch ME
    error('Pathfinding failed: %s', ME.message);
end

%% STEP 7: Display the result
close all;
figure;
imshow(~M); hold on;
plot(c, r, 'b-', 'LineWidth', 2);
plot(ci, ri, 'co', 'MarkerSize', 10, 'LineWidth', 2);
plot(cf, rf, 'mo', 'MarkerSize', 10, 'LineWidth', 2);
plot(fire_coords(:,2), fire_coords(:,1), 'rx', 'MarkerSize', 10, 'LineWidth', 2);
viscircles(fire_coords(:, [2 1]), repmat(radii, size(fire_coords,1), 1), ...
           'Color', 'r', 'LineStyle', '--', 'LineWidth', 1);
plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
title('Computed Safe Path');
legend({'Path', 'Start', 'Goal', 'Fire Centers', 'Person'}, ...
       'Location', 'southoutside', 'Orientation', 'horizontal');

