import pygame
import math
import serial
import json
from serial import SerialException

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1500, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LiDAR Sensor Dashboard with Controls")

# Colors
GREEN = (98, 245, 31)
DARK_GREEN = (0, 4, 0, 4)
RED = (255, 10, 10)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
SLIDER_COLOR = (70, 70, 70)
SLIDER_HANDLE_COLOR = (150, 150, 150)

# Sensor data
sensor_data = {
    "Distance": 0,
    "Temperature": 0.0,
    "Pressure": 0.0,
    "Altitude": 0.0,
    "Acceleration_X": 0.0,
    "Acceleration_Y": 0.0,
    "Acceleration_Z": 0.0,
    "Rotation_X": 0.0,
    "Rotation_Y": 0.0,
    "Rotation_Z": 0.0
}

# Radar parameters (all in cm)
iAngle = 0
max_distance = 400  # 8 meters (800cm)
min_distance = 2    # 2cm minimum distance
sweep_speed = 1     # Default speed (degrees per frame)

# Sliders
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.handle_rect = pygame.Rect(x, y - 5, 20, h + 10)
        self.min = min_val
        self.max = max_val
        self.val = initial_val
        self.label = label
        self.dragging = False
        self.update_handle_pos()

    def update_handle_pos(self):
        relative_val = (self.val - self.min) / (self.max - self.min)
        self.handle_rect.x = self.rect.x + int(relative_val * self.rect.width) - 10

    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, SLIDER_COLOR, self.rect, border_radius=5)
        # Draw slider handle
        pygame.draw.rect(surface, SLIDER_HANDLE_COLOR, self.handle_rect, border_radius=5)
        # Draw label and value
        label_text = font.render(f"{self.label}:", True, WHITE)
        value_text = font.render(f"{self.val:.1f}", True, WHITE)
        surface.blit(label_text, (self.rect.x - 150, self.rect.y - 5))
        surface.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y - 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Calculate new value based on mouse position
            mouse_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            relative_pos = (mouse_x - self.rect.x) / self.rect.width
            self.val = self.min + relative_pos * (self.max - self.min)
            self.update_handle_pos()
            return True
        return False

# Create sliders (updated for cm)
max_dist_slider = Slider(WIDTH - 400, 50, 200, 10, 50, 400, max_distance, "Max Distance (cm)")
speed_slider = Slider(WIDTH - 400, 100, 200, 10, 0.1, 5, sweep_speed, "Sweep Speed (°/frame)")

# Fonts
try:
    font = pygame.font.SysFont('consolas', 20)
    medium_font = pygame.font.SysFont('consolas', 24)
    large_font = pygame.font.SysFont('consolas', 30)
    title_font = pygame.font.SysFont('consolas', 40)
except:
    font = pygame.font.SysFont('arial', 20)
    medium_font = pygame.font.SysFont('arial', 24)
    large_font = pygame.font.SysFont('arial', 30)
    title_font = pygame.font.SysFont('arial', 40)

# Serial connection
try:
    ser = serial.Serial('COM3', 115200, timeout=0.1)
except SerialException:
    print("Could not open serial port")
    ser = None

def draw_radar():
    center_x = WIDTH // 3
    center_y = int(0.8 * HEIGHT)
    
    # Draw arc lines based on current max distance (in meters for display)
    arc_distances_m = [max_distance * 0.25 / 100, max_distance * 0.5 / 100, 
                      max_distance * 0.75 / 100, max_distance / 100]
    
    for i, distance_m in enumerate(arc_distances_m):
        coeff = ((i+1)/4) * 0.7  # 4 arcs evenly spaced
        pygame.draw.arc(screen, GREEN, 
                       (center_x - (coeff * WIDTH//2), center_y - (coeff * WIDTH//2), 
                        coeff * WIDTH, coeff * WIDTH), 
                       math.pi, 2 * math.pi, 2)
        
        # Draw distance labels in meters
        if i < 3:  # Don't draw label for max distance (it's shown elsewhere)
            label_x = center_x + (coeff * WIDTH//2) * math.cos(math.pi/4)
            label_y = center_y - (coeff * WIDTH//2) * math.sin(math.pi/4) - 20
            label_text = font.render(f"{distance_m:.1f}m", True, GREEN)
            screen.blit(label_text, (label_x, label_y))

def draw_object():
    center_x = WIDTH // 3
    center_y = int(0.8 * HEIGHT)
    distance = sensor_data["Distance"]  # Already in cm
    
    if min_distance <= distance <= max_distance:
        # Scale distance to radar display
        distance_ratio = distance / max_distance
        pixsDistance = int(distance_ratio * 0.7 * (WIDTH//2))
        
        rad_angle = math.radians(iAngle)
        cos_val = math.cos(rad_angle)
        sin_val = math.sin(rad_angle)
        
        x1 = center_x + int(pixsDistance * cos_val)
        y1 = center_y - int(pixsDistance * sin_val)
        
        # Draw object point
        pygame.draw.circle(screen, RED, (x1, y1), 5)
        
        # Draw line to object
        x2 = center_x + int(0.35 * WIDTH * cos_val)
        y2 = center_y - int(0.35 * WIDTH * sin_val)
        pygame.draw.line(screen, RED, (x1, y1), (x2, y2), 2)

def draw_sweep_line():
    center_x = WIDTH // 3
    center_y = int(0.8 * HEIGHT)
    
    rad_angle = math.radians(iAngle)
    x = center_x + int(0.65 * (WIDTH//3) * math.cos(rad_angle))
    y = center_y - int(0.65 * (WIDTH//3) * math.sin(rad_angle))
    
    pygame.draw.line(screen, (30, 250, 60), (center_x, center_y), (x, y), 3)

def draw_sensor_data():
    # Draw background panel
    panel_width = WIDTH // 2.5
    pygame.draw.rect(screen, (20, 20, 40), (WIDTH - panel_width - 20, 20, panel_width, HEIGHT - 40))
    pygame.draw.rect(screen, GREEN, (WIDTH - panel_width - 20, 20, panel_width, HEIGHT - 40), 2)
    
    # Title
    title = title_font.render("LiDAR Sensor Data & Controls", True, GREEN)
    screen.blit(title, (WIDTH - panel_width - 20 + (panel_width - title.get_width()) // 2, 30))
    
    # Draw sliders
    max_dist_slider.draw(screen)
    speed_slider.draw(screen)
    
    # Data rows
    y_offset = 150
    row_height = 40
    
    def draw_data_row(label, value, unit=""):
        nonlocal y_offset
        label_text = medium_font.render(f"{label}:", True, WHITE)
        value_text = medium_font.render(f"{value} {unit}", True, BLUE)
        screen.blit(label_text, (WIDTH - panel_width, y_offset))
        screen.blit(value_text, (WIDTH - panel_width + 200, y_offset))
        y_offset += row_height
    
    # Display all sensor data (distance in cm)
    draw_data_row("Distance", sensor_data["Distance"], "cm")
    draw_data_row("Temperature", f"{sensor_data['Temperature']:.2f}", "°C")
    draw_data_row("Pressure", f"{sensor_data['Pressure']:.2f}", "Pa")
    draw_data_row("Altitude", f"{sensor_data['Altitude']:.2f}", "m")
    
    # Acceleration data
    y_offset += 20
    draw_data_row("Acceleration X", f"{sensor_data['Acceleration_X']:.4f}", "m/s²")
    draw_data_row("Acceleration Y", f"{sensor_data['Acceleration_Y']:.4f}", "m/s²")
    draw_data_row("Acceleration Z", f"{sensor_data['Acceleration_Z']:.4f}", "m/s²")
    
    # Rotation data
    y_offset += 20
    draw_data_row("Rotation X", f"{sensor_data['Rotation_X']:.4f}", "rad")
    draw_data_row("Rotation Y", f"{sensor_data['Rotation_Y']:.4f}", "rad")
    draw_data_row("Rotation Z", f"{sensor_data['Rotation_Z']:.4f}", "rad")

def draw_status():
    # Black background for status area
    pygame.draw.rect(screen, BLACK, (0, int(0.9 * HEIGHT), WIDTH, HEIGHT))
    
    # Status text
    distance = sensor_data["Distance"]
    in_range = min_distance <= distance <= max_distance
    
    status_text = large_font.render("Status:", True, GREEN)
    screen.blit(status_text, (20, int(0.92 * HEIGHT)))
    
    range_text = large_font.render(
        f"Object: {'In Range' if in_range else 'Out of Range'}",
        True, GREEN if in_range else RED
    )
    screen.blit(range_text, (150, int(0.92 * HEIGHT)))
    
    angle_text = large_font.render(f"Scan Angle: {iAngle}°", True, GREEN)
    screen.blit(angle_text, (500, int(0.92 * HEIGHT)))
    
    if in_range:
        distance_text = large_font.render(f"Distance: {distance} cm (Max: {max_distance}cm)", True, GREEN)
        screen.blit(distance_text, (850, int(0.92 * HEIGHT)))

def parse_lidar_data(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None

def read_serial():
    if ser and ser.in_waiting > 0:
        try:
            data = ser.readline().decode('utf-8').strip()
            parsed = parse_lidar_data(data)
            if parsed:
                for key in sensor_data:
                    if key in parsed:
                        sensor_data[key] = parsed[key]
        except Exception as e:
            print(f"Serial error: {e}")

def main():
    global iAngle, max_distance, sweep_speed
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle slider events
            if max_dist_slider.handle_event(event):
                max_distance = int(max_dist_slider.val)
            if speed_slider.handle_event(event):
                sweep_speed = speed_slider.val
        
        # Read from serial port
        read_serial()
        
        # Update sweep angle with current speed
        iAngle = (iAngle + sweep_speed) % 180
        
        # Clear screen with semi-transparent overlay for trail effect
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 10))
        screen.blit(overlay, (0, 0))
        
        # Draw all components
        draw_radar()
        draw_sweep_line()
        draw_object()
        draw_sensor_data()
        draw_status()
        
        pygame.display.flip()
        clock.tick(30)  # 30 FPS
    
    if ser:
        ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()