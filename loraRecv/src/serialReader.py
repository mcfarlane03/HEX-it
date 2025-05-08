import numpy as np
import serial
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from datetime import datetime
import os
import scipy.io as sio  
import time

class RoomMapper:
    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=115200):
        self.serial = serial.Serial(serial_port, baud_rate)
        self.scan_data = []
        self.robot_pose = [0, 0, 0]  # x, y, theta
        
        # Initialize visualization
        plt.ion()
        self.fig = plt.figure(figsize=(15, 8))
        
        # Room map (top view)
        self.ax_map = self.fig.add_subplot(231)
        self.ax_map.set_title('Room Map (Top View)')
        
        # 3D visualization
        self.ax_3d = self.fig.add_subplot(232, projection='3d')
        self.ax_3d.set_title('3D Point Cloud')
        
        # IMU data plots
        self.ax_accel = self.fig.add_subplot(234)
        self.ax_gyro = self.fig.add_subplot(235)
        self.ax_alt = self.fig.add_subplot(236)
        
        plt.tight_layout()
        
        # Create data directory
        self.data_dir = f"room_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.data_dir, exist_ok=True)

    def process_scan(self, data):
        """Process incoming sensor data packet"""
        # Convert polar to cartesian coordinates
        angles = np.array(data['angles'])
        distances = np.array(data['distances'])
        altitudes = np.array(data['altitudes'])
        
        # Apply robot pose transformation
        x = distances * np.cos(np.radians(angles))
        y = distances * np.sin(np.radians(angles))
        z = altitudes
        
        # Update visualizations
        self._update_map(x, y, data['humanDetected'])
        self._update_3d(x, y, z)
        self._update_imu(data)
        
        # Save data point
        self._save_data_point(data)

    def _update_map(self, x, y, human_detected):
        self.ax_map.clear()
        self.ax_map.scatter(x, y, c='b', s=1)
        if human_detected:
            self.ax_map.plot(0, 0, 'r*', markersize=10, label='Human Detected')
        self.ax_map.grid(True)
        self.ax_map.set_title('Room Map (Top View)')
        self.ax_map.axis('equal')

    def _update_3d(self, x, y, z):
        self.ax_3d.clear()
        self.ax_3d.scatter(x, y, z, c='b', s=1)
        self.ax_3d.set_title('3D Point Cloud')
        self.ax_3d.set_xlabel('X (mm)')
        self.ax_3d.set_ylabel('Y (mm)')
        self.ax_3d.set_zlabel('Z (mm)')

    def _update_imu(self, data):
        # Plot accelerometer data
        self.ax_accel.clear()
        self.ax_accel.plot(data['accelX'], label='X')
        self.ax_accel.plot(data['accelY'], label='Y')
        self.ax_accel.plot(data['accelZ'], label='Z')
        self.ax_accel.set_title('Accelerometer')
        self.ax_accel.legend()
        
        # Plot gyroscope data
        self.ax_gyro.clear()
        self.ax_gyro.plot(data['gyroX'], label='X')
        self.ax_gyro.plot(data['gyroY'], label='Y')
        self.ax_gyro.plot(data['gyroZ'], label='Z')
        self.ax_gyro.set_title('Gyroscope')
        self.ax_gyro.legend()
        
        plt.draw()
        plt.pause(0.01)

    def _save_data_point(self, data):
        """Save scan data to CSV"""
        df = pd.DataFrame({
            'timestamp': [data['timestamp']],
            'angle': [data['angles'][0]],
            'distance': [data['distances'][0]],
            'altitude': [data['altitudes'][0]],
            'human_detected': [data['humanDetected']],
            'accel_x': [data['accelX'][0]],
            'accel_y': [data['accelY'][0]],
            'accel_z': [data['accelZ'][0]],
            'gyro_x': [data['gyroX'][0]],
            'gyro_y': [data['gyroY'][0]],
            'gyro_z': [data['gyroZ'][0]]
        })
        
        csv_file = os.path.join(self.data_dir, 'scan_data.csv')
        df.to_csv(csv_file, mode='a', header=not os.path.exists(csv_file), index=False)

    def run(self):
        """Main loop to read and process serial data"""
        print("Starting room mapping...")
        try:
            while True:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode().strip()
                    try:
                        data = json.loads(line)
                        self.process_scan(data)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {line}")
        except KeyboardInterrupt:
            print("\nMapping stopped. Saving data...")
            plt.savefig(os.path.join(self.data_dir, 'final_map.png'))