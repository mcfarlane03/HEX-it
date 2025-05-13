% main_pathfinder.m
% Load a blueprint and find a path avoiding fire zones toward detected people.

clear; clc; close all;

%% STEP 1: Load and preprocess the blueprint image
img = imread('testerplan2.png');        % Replace with your blueprint file
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
%% STEP 3: Simulate a Person in the Center of the Map
% Automatically find the center-most free spot

center_row = round(size(M, 1) / 2);
center_col = round(size(M, 2) / 2);
found_persons = [];

% Search outward in a spiral until a free (non-obstacle) location is found
max_radius = max(size(M));
found = false;
for radius = 0:max_radius
    for dx = -radius:radius
        for dy = -radius:radius
            row = center_row + dy;
            col = center_col + dx;
            if row > 0 && row <= size(M,1) && col > 0 && col <= size(M,2)
                if M(row, col) == 0
                    person_row = row;
                    person_col = col;
                    found = true;
                    break;
                end
            end
        end
        if found, break; end
    end
    if found, break; end
end

if ~found
    error('❌ No free space found near the center!');
end

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
for k = 1:size(found_persons, 1)
    pos = found_persons(k, :);
    rectangle('Position', [pos(2)-3, pos(1)-3, 6, 6], 'EdgeColor', 'r', 'LineWidth', 2);
end
title('Map with Fire Zones and Person (Click START Point)');

 legend([h_fire, h_circles, h_person], {'Fire Centers', 'Fire Region ','Person'}, ...
        'Location','southoutside','Orientation','horizontal');

%% STEP 5: Define start and end points
continue_pathfinding = true;

while continue_pathfinding
    %% STEP 5: Select Start and Goal
    valid = false;
    while ~valid
        imshow(~M); hold on;
        status_text = text(10, size(M,1)+10, '', 'Color', 'white', 'FontSize', 12, 'FontWeight', 'bold');

        % Plot fire and person again
        plot(fire_coords(:,2), fire_coords(:,1), 'rx', 'MarkerSize', 8, 'LineWidth', 2);
        plot(fire_affected_zones(:,2), fire_affected_zones(:,1), 'ro', 'MarkerSize', 4);
        plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
        title('Click START point (white = free)');
        legend({'Fire Centers', 'Fire Region', 'Person'}, ...
            'Location','southoutside','Orientation','horizontal');

        [c_start, r_start] = ginput(1);
        ri = round(r_start); ci = round(c_start);

        if ri > 0 && ri <= size(M,1) && ci > 0 && ci <= size(M,2)
            is_in_fire_zone = any(ismember(fire_affected_zones, [ri ci], 'rows'));
            if M(ri, ci) == 0 && ~is_in_fire_zone
                valid = true;
                disp(['✅ Start selected at (' num2str(ri) ',' num2str(ci) ')']);
                set(status_text, 'String', 'Start Selected', 'Color', 'green');
                pause(1.5);
                set(status_text, 'String', '');
            else
                disp('❌ Invalid START! Must be free and not in fire zone.');
                set(status_text, 'String','❌ Invalid START!', 'Color', 'magenta');
                pause(1.5); set(status_text, 'String', '');
            end
        end
    end

    valid = false;
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
                pause(1.0);
                set(status_text, 'String', 'Wait While We Generating Path', 'Color', 'green');
                pause(1.5);  % Wait 1.5 seconds
                set(status_text, 'String', '');  % Clear the message
            else
                disp('❌ Invalid GOAL! Must be free and not in fire zone.');
                set(status_text, 'String','❌ Invalid GOAL!', 'Color', 'magenta');
                pause(1.5); set(status_text, 'String', '');
            end
        end
    end
%% STEP 6: Call your shpath function
% Run shortest path algorithm
try
    [r, c, H] = shpath(M, ri, ci, rf, cf);  % custom pathfinding 

    if rf == person_row && cf == person_col
        found_persons(end+1, :) = [person_row, person_col];
    end
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

    % --- Ask user to save image ---
    choice = questdlg('Do you want to save a screenshot of this path?', ...
        'Save Image?', 'Yes', 'No', 'No');
    if strcmp(choice, 'Yes')
        [file, path] = uiputfile('*.png', 'Save Image As');
        if ischar(file)
            saveas(gcf, fullfile(path, file));
            disp(['✅ Screenshot saved to: ' fullfile(path, file)]);
        end
    end

    % --- Ask to restart ---
    cont_choice = questdlg('Do you want to select a new START and GOAL?', ...
        'Continue?', 'Yes', 'No', 'Yes');
    if strcmp(cont_choice, 'No')
        continue_pathfinding = false;
        disp('👋 Exiting pathfinding...');
    end

    close(gcf); % Close path display figure before next loop
end

