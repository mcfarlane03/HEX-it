% main_pathfinder.mlegend
% Load a blueprint and find a path avoiding fire zones toward detected people.

clear; clc; close all;

%% STEP 1: Load and preprocess the blueprint image
img = imread('slam_map.png');        % Replace with your blueprint file
gray = rgb2gray(img);                 % Convert to grayscale
% bw = imcomplement(imbinarize(rgb2gray(img))); % Convert to binary (adjust as needed)
% M = bw; % M is the obstacle map: 1 = blocked, 0 = free               
bw = imbinarize(gray);         % White = free, black = wall
M = imcomplement(bw);          % M: 1 = obstacle, 0 = free space
                               
% imshow(M); title('Initial Map (WhitFe = Free, Black = Obstacle)');

% Step 1.2: Detect red (fire) and green (person) regions
red_mask = img(:,:,1) > 150 & img(:,:,2) < 100 & img(:,:,3) < 100;
green_mask = img(:,:,1) < 100 & img(:,:,2) > 150 & img(:,:,3) < 100;

% Add fire areas to obstacle map
fire_pixels = find(red_mask);
M(fire_pixels) = 1;

% Find fire coordinates
[fire_y, fire_x] = find(red_mask);
fire_coords = [fire_y, fire_x];

% Find person coordinates
[person_y, person_x] = find(green_mask);
found_people = [];

has_person = ~isempty(person_y);
if has_person
    person_row = person_y;
    person_col = person_x;
end


fire_affected_zones = []; % Reset it to track all cells affected by fire zones

for i = 1:size(fire_coords, 1)
    row = fire_coords(i,1);
    col = fire_coords(i,2);
    
    % Mark fire center + 8-neighbors (3x3 area)
    for dr = -1:1
        for dc = -1:1
            r2 = row + dr;
            c2 = col + dc;
            if r2 > 0 && r2 <= size(M,1) && c2 > 0 && c2 <= size(M,2)
                M(r2, c2) = 1; % Mark as obstacle
                fire_affected_zones(end+1, :) = [r2, c2];
            end
        end
    end
end


%% STEP 2: Visualize detected map
fig1 = figure;
imshow(~M); hold on;

% Fire centers (red x)
if ~isempty(fire_coords)
    h_fires = plot(fire_x, fire_y, 'rx', 'MarkerSize', 8, 'LineWidth', 2);
else
    h_fires = plot(NaN, NaN, 'rx'); % Dummy for legend
end

% Person (green circle)
if has_person
    h_person = plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
else
    h_person = plot(NaN, NaN, 'go'); % Dummy for legend
end

if ~isempty(found_people)
    for k = 1:size(found_people,1)
        pr = found_people(k,1);
        pc = found_people(k,2);
        rectangle('Position', [pc - 10, pr - 10, 20, 20], ...
                  'EdgeColor', 'r', 'LineWidth', 2);
    end
end

title('Map with Detected Fires and Person (Green)');
legend([h_fires, h_person], {'Fires (Red)', 'Person (Green)'}, ...
    'Location','southoutside','Orientation','horizontal');

%% STEP 3: Define start and end points
continue_flag = true;
while continue_flag
valid = false;
while ~valid

    imshow(~M); hold on;    

    status_text = text(10, size(M,1)+10, '', 'Color', 'white', 'FontSize', 12, 'FontWeight', 'bold');
    
    % Fire centers
    if ~isempty(fire_coords)
        h_fires = plot(fire_coords(:,2), fire_coords(:,1), 'rx', 'MarkerSize', 8, 'LineWidth', 2);
    else
        h_fires = plot(NaN, NaN, 'rx');
    end
    
    % Fire region
    if ~isempty(fire_affected_zones)
        h_circles = plot(fire_zone_cols, fire_zone_rows, 'ro', 'MarkerSize', 4);
    else
        h_circles = plot(NaN, NaN, 'ro');
    end
    
    % Person
    if has_person
        h_person = plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
    else
        h_person = plot(NaN, NaN, 'go');
    end

     if ~isempty(found_people)
        for k = 1:size(found_people,1)
            pr = found_people(k,1);
            pc = found_people(k,2);
            rectangle('Position', [pc - 10, pr - 10, 20, 20], ...
                      'EdgeColor', 'r', 'LineWidth', 2);
        end
    end

    title('Click START point (white = free)');

    legend([h_fires, h_circles, h_person],{'Fire Centers', 'Fire Region ','Person'}, ...
        'Location','southoutside','Orientation','horizontal');

    [c_start, r_start] = ginput(1);
    ri = round(r_start); ci = round(c_start);

     if ri > 0 && ri <= size(M,1) && ci > 0 && ci <= size(M,2)
        if isempty(fire_affected_zones)
            is_in_fire_zone = false;
        else
            is_in_fire_zone = any(ismember(fire_affected_zones, [ri ci], 'rows'));
        end
        if M(ri, ci) == 0 && ~is_in_fire_zone
            valid = true;
            disp(['✅ Start selected at (' num2str(ri) ',' num2str(ci) ')']);
            set(status_text, 'String', 'Start Selected', 'Color', 'green');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        else
            disp('❌ Invalid START! Must be free and not in fire zone.');
            set(status_text, 'String', '❌ Invalid START! Must be free and not in fire zone.', 'Color', 'magenta');
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
        if isempty(fire_affected_zones)
            is_in_fire_zone = false;
        else
            is_in_fire_zone = any(ismember(fire_affected_zones, [ri ci], 'rows'));
        end
        if M(rf, ci) == 0 && ~is_in_fire_zone
            valid = true;
            disp(['✅ Goal selected at (' num2str(ri) ',' num2str(ci) ')']);
            set(status_text, 'String', 'Goal Selected.', 'Color', 'green');
            pause(1.0);
            set(status_text, 'String', 'Wait While We Generating Path', 'Color', 'green');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        else
            disp('❌ Invalid GOAL! Must be free and not in fire zone.');
            set(status_text, 'String', '❌ Invalid GOAL! Must be free and not in fire zone.', 'Color', 'magenta');
            pause(1.5);  % Wait 1.5 seconds
            set(status_text, 'String', '');  % Clear the message
        end
    end
end

%% STEP 4: Call your shpath function
% Run shortest path algorithm
try
    [r, c, H] = shpath(M, ri, ci, rf, cf);  % Your custom pathfinding function
catch ME
    error('Pathfinding failed: %s', ME.message);
end

%% STEP 5: Display result
    close(fig1);
    fig_result = figure;
    imshow(~M); hold on;
    plot(c, r, 'b-', 'LineWidth', 2);         % Path
    plot(ci, ri, 'co', 'MarkerSize', 10, 'LineWidth', 2);  % Start
    plot(cf, rf, 'mo', 'MarkerSize', 10, 'LineWidth', 2);  % Goal

    if ~isempty(fire_coords)
        plot(fire_x, fire_y, 'rx', 'MarkerSize', 8, 'LineWidth', 2);
    end
    if has_person
        plot(person_col, person_row, 'go', 'MarkerSize', 10, 'LineWidth', 2);
    end

    legend({'Path', 'Start', 'Goal', 'Fire Centers', 'Person'}, ...
        'Location', 'southoutside', 'Orientation', 'horizontal');
    title('Path Result');

    %% STEP 6: Prompt for screenshot and repeat
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
        'Continue?', 'Yes', 'No', 'No');

    if strcmp(cont_choice, 'Yes')
        continue_flag = true;
    else
        continue_flag = false;

        disp('👋 Exiting pathfinding...');
    end

    close(gcf); % Close path display figure before next loop
end