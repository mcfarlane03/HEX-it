import serial
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import time
from collections import deque

# Configuration
PORT = 'COM3'  # Change this to match your Arduino's port
BAUD_RATE = 115200
MAX_POINTS = 500  # Maximum number of points to keep
PLOT_REFRESH_RATE = 100  # ms

HISTORY_SIZE = 500  # For orientation history
UPDATE_RATE_HZ = 100

UPDATE_INTERVAL_MS = 1000 / UPDATE_RATE_HZ
# Setup serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Give time for connection to establish

# Data storage
x_points = deque(maxlen=MAX_POINTS)
y_points = deque(maxlen=MAX_POINTS)
orientation_history = deque(maxlen=HISTORY_SIZE) # Track orientation over time

current_angle = 0  # Start angle in degrees
current_position = (0, 0)
last_timestamp = 0

# Timing Tracking
last_update_time = 0
last_processed_timestamp = 0

# Setup plot
fig, ax = plt.subplots(figsize=(12, 10))
ax.set_aspect('equal')
line, = ax.plot([], [], 'g-', linewidth=2)  # Green line like in your image
scatter = ax.scatter([], [], c='r', s=50)  # Red dot for current measurement point

# Device marker at origin
device = ax.scatter([0], [0], c='blue', s=100, marker='s')  # Blue square for the device

# Plot limits - adjust based on your room size (in cm)
room_radius = 300  # Maximum expected distance in cm
ax.set_xlim(-room_radius, room_radius)
ax.set_ylim(-room_radius, room_radius)
ax.grid(True)
ax.set_title('Room Mapping (Device at Origin)')
ax.set_xlabel('X (cm)')
ax.set_ylabel('Y (cm)')

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='g', lw=2, label='Room Outline'),
    plt.scatter([0], [0], c='r', s=50, label='Current Measurement'),
    plt.scatter([0], [0], c='blue', s=100, marker='s', label='Device Position')
]
ax.legend(handles=legend_elements, loc='upper right')

# Function to convert polar to cartesian coordinates
def polar_to_cartesian(distance, angle_deg):
    angle_rad = math.radians(angle_deg)
    x = distance * math.cos(angle_rad)
    y = distance * math.sin(angle_rad)
    return x, y

# Initialization function
def init():
    line.set_data([], [])
    scatter.set_offsets(np.c_[[], []])
    return line, scatter, device

def process_data():
    global current_angle, x_points, y_points, orientation_history, last_processed_timestamp, current_position
    
    try:
        # Read data from serial
        if ser.in_waiting > 0:
            data_line = ser.readline().decode('utf-8').strip()
            if data_line:
                try:
                    data = json.loads(data_line)

                    if data['Timestamp'] > last_processed_timestamp:
                                update_point_cloud(data)
                                last_processed_timestamp = data['Timestamp']
                                return True
                    
                except json.JSONDecodeError:
                    print("Invalid JSON received")
    
    except Exception as e:
        print(f"Data processing error: {e}")
    
    return False

def update_point_cloud(data):
    """Update point cloud based on sensor data (from code 2)"""
    global current_angle, x_points, y_points, orientation_history, current_position
    
    if data['Distance'] <= 0:
        return
    # Extract distance and rotation data
    distance = data['Distance']
    #rotation_z = data['Rotation_Z']  # Z-axis rotation in radians/sec
                    
    # Update current angle
    current_angle = data['Yaw']
    # Update angle based on rotation
    # Adjust the scaling factor as needed
    #angle_change = math.degrees(rotation_z) * 10
    #current_angle = (current_angle + angle_change) % 360
                    
    # Convert distance and angle to x,y coordinates
    dx, dy = polar_to_cartesian(distance, current_angle)
                    
    # Add points to lists
    x_points.append(dx)
    y_points.append(dy)
    current_position = (dx, dy)
    
    #Store orientation history
    orientation_history.append({
        'timestamp': data['Timestamp'],
        'angle': current_angle
    })
    
    # Debug output
    print(f"Point Added: ({dx:.2f}, {dy:.2f}), Angle: {current_angle:.2f}°, Timestamp: {data['Timestamp']}")
    
    
# Function to read data from serial and update the plot
def update(frame):   
    data_received = process_data()
    
    # Update point cloud only if new data was received
    if data_received and x_points and y_points:
        # Update the line data
        line.set_data(x_points, y_points)
    
        # Update the current measurement point marker
        scatter.set_offsets(np.c_[[x_points[-1]], [y_points[-1]]])
    
    # Adjust plot limits if needed
    if x_points and y_points:
        max_range = max(
            max(abs(min(x_points)), abs(max(x_points))),
            max(abs(min(y_points)), abs(max(y_points)))
        ) * 1.1  # Add 10% margin
        
        if max_range > 50:  # Only resize if we have significant data
            ax.set_xlim(-max_range, max_range)
            ax.set_ylim(-max_range, max_range)
    
    return line, scatter, device

# Create animation
ani = FuncAnimation(fig, update, frames=None, 
                    init_func=init, blit=True, interval=PLOT_REFRESH_RATE)

# Show the plot
plt.tight_layout()
plt.show()

# Clean up
def close_connection():
    ser.close()
    print("Serial connection closed")

# Register cleanup function
import atexit
atexit.register(close_connection)