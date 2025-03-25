import serial
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import time

# Configuration
PORT = 'COM3'  # Change this to match your Arduino's port
BAUD_RATE = 115200
MAX_POINTS = 500  # Maximum number of points to keep
PLOT_REFRESH_RATE = 100  # ms

# Setup serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Give time for connection to establish

# Data storage
x_points = []
y_points = []
current_angle = 0  # Start angle in degrees

# Setup plot
fig, ax = plt.subplots(figsize=(10, 10))
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

# Function to read data from serial and update the plot
def update(frame):
    global current_angle, x_points, y_points
    
    try:
        # Read data from serial
        if ser.in_waiting > 0:
            data_line = ser.readline().decode('utf-8').strip()
            if data_line:
                data = json.loads(data_line)
                
                # Extract distance and rotation data
                distance = data['Distance']
                rotation_z = data['Rotation_Z']  # Z-axis rotation in radians/sec
                
                # Update angle based on rotation
                # Adjust the scaling factor as needed
                angle_change = math.degrees(rotation_z) * 10
                current_angle = (current_angle + angle_change) % 360
                
                # Convert distance and angle to x,y coordinates
                dx, dy = polar_to_cartesian(distance, current_angle)
                
                # Add points to lists
                x_points.append(dx)
                y_points.append(dy)
                
                # Keep lists at reasonable size
                if len(x_points) > MAX_POINTS:
                    x_points = x_points[-MAX_POINTS:]
                    y_points = y_points[-MAX_POINTS:]
                
                # Debug
                print(f"Angle: {current_angle:.1f}°, Distance: {distance} cm, Rotation_Z: {rotation_z}")
                
    except Exception as e:
        print(f"Error: {e}")
    
    # Update the line data
    line.set_data(x_points, y_points)
    
    # Update the current measurement point marker
    if x_points and y_points:
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