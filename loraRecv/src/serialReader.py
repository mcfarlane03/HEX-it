import numpy as np
import math
import open3d as o3d
from collections import deque
from scipy.spatial.transform import Rotation as R
import time
import json
import serial
from serial import SerialException

class LidarMappingSystem:
    def __init__(self, serial_port='COM3', baud_rate=115200):
        # Sensor data storage
        self.sensor_data = {
            "Timestamp": None,
            "Distance": 0,
            "Temp": 0.0,
            "Pressure": 0.0,
            "Alti": 0.0,
            "Accel_X": 0.0,
            "Accel_Y": 0.0,
            "Accel_Z": 0.0,
            "Rotat_X": 0.0,
            "Rotat_Y": 0.0,
            "Rotat_Z": 0.0,
            "Human": False
        }
        
        # Mapping parameters
        self.keyframes = deque(maxlen=1000)
        self.current_pose = np.eye(4)  # Identity matrix as initial pose
        self.map_points = []
        self.last_update_time = time.time()
        
        # LiDAR parameters
        self.min_distance = 2.0  # 2cm
        self.max_distance = 400.0  # 4m
        self.current_angle = 0
        self.sweep_speed = 1  # Degrees per update
        
        # Initialize visualization
        self.init_visualization()
        
        # Initialize serial connection
        try:
            self.ser = serial.Serial(serial_port, baud_rate, timeout=0.1)
            print(f"Connected to {serial_port} at {baud_rate} baud")
        except SerialException as e:
            print(f"Could not open serial port: {e}")
            print("Running in simulation mode")
            self.ser = None

    def init_visualization(self):
        """Initialize Open3D visualization window"""
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="3D LiDAR Mapping", width=1280, height=720)
        
        # Add coordinate frame and point cloud
        self.pcd = o3d.geometry.PointCloud()
        self.coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=20.0)
        
        # Add geometries to visualizer
        self.vis.add_geometry(self.pcd)
        self.vis.add_geometry(self.coordinate_frame)
        
        # Set default viewpoint
        self.vis.get_view_control().set_zoom(0.8)
        self.vis.get_render_option().point_size = 2.0

    def read_sensor_data(self):
        """Read and parse sensor data from serial port"""
        if self.ser and self.ser.in_waiting > 0:
            try:
                data = self.ser.readline().decode('utf-8').strip()
                if data:
                    try:
                        parsed_data = json.loads(data)
                        # Update sensor data with available values
                        for key in self.sensor_data:
                            if key in parsed_data:
                                self.sensor_data[key] = parsed_data[key]
                        return True
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON: {data}")
            except Exception as e:
                print(f"Serial read error: {e}")
        return False

    def scan_to_point(self, angle_deg, distance_cm):
        """Convert a 2D LiDAR measurement to 3D point using altitude"""
        if distance_cm < self.min_distance or distance_cm > self.max_distance:
            return None
        
        # Convert to radians and calculate x,y coordinates
        angle_rad = math.radians(angle_deg)
        x = distance_cm * math.cos(angle_rad)
        y = distance_cm * math.sin(angle_rad)
        z = self.sensor_data["Altitude"] * 100  # Convert meters to cm
        
        return np.array([x, y, z, 1.0])  # Homogeneous coordinates

    def estimate_pose(self, dt):
        """Update pose estimation using IMU data (dead reckoning)"""
        # Extract rotation rates and accelerations
        gyro = np.array([
            self.sensor_data["Rotation_X"],
            self.sensor_data["Rotation_Y"],
            self.sensor_data["Rotation_Z"]
        ])
        
        accel = np.array([
            self.sensor_data["Acceleration_X"],
            self.sensor_data["Acceleration_Y"],
            self.sensor_data["Acceleration_Z"]
        ])
        
        # Calculate rotation update (simple integration)
        rotation_update = R.from_euler('xyz', gyro * dt).as_matrix()
        
        # Apply rotation to current orientation
        self.current_pose[:3, :3] = self.current_pose[:3, :3] @ rotation_update
        
        # Transform acceleration to world frame
        accel_world = self.current_pose[:3, :3] @ accel
        
        # Simple double integration for position (gravity should be properly handled in real implementation)
        self.current_pose[:3, 3] += accel_world * dt**2

    def should_create_keyframe(self):
        """Determine if we should create a new keyframe based on movement"""
        if not self.keyframes:
            return True  # Always create the first keyframe
        
        # Get the last keyframe's pose
        last_kf_pose = self.keyframes[-1]["pose"]
        
        # Calculate translation difference
        translation_diff = np.linalg.norm(self.current_pose[:3, 3] - last_kf_pose[:3, 3])
        
        # Calculate rotation difference
        rot1 = R.from_matrix(self.current_pose[:3, :3])
        rot2 = R.from_matrix(last_kf_pose[:3, :3])
        rotation_diff = np.linalg.norm(rot1.as_rotvec() - rot2.as_rotvec())
        
        # Check altitude difference
        altitude_diff = abs(self.sensor_data["Altitude"] - self.keyframes[-1]["altitude"])
        
        # Create keyframe if moved more than 10cm, rotated more than 5 degrees, or altitude changed more than 10cm
        return (translation_diff > 10.0 or 
                rotation_diff > math.radians(5.0) or 
                altitude_diff > 0.1)

    def create_keyframe(self, point):
        """Create and store a new keyframe"""
        if point is None:
            return
        
        # Store keyframe data
        keyframe = {
            "pose": self.current_pose.copy(),
            "point": point,
            "altitude": self.sensor_data["Altitude"],
            "timestamp": time.time()
        }
        
        self.keyframes.append(keyframe)
        
        # Add point to global map
        global_point = self.current_pose @ point
        self.map_points.append(global_point[:3])  # Only store x,y,z

    def update_visualization(self):
        """Update the 3D visualization"""
        if not self.map_points:
            return
            
        # Update point cloud with current map points
        self.pcd.points = o3d.utility.Vector3dVector(np.array(self.map_points))
        
        # Set colors (optional)
        colors = np.ones((len(self.map_points), 3)) * np.array([0.5, 0.5, 1.0])  # Blue points
        self.pcd.colors = o3d.utility.Vector3dVector(colors)
        
        # Update coordinate frame to current position
        self.coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=20.0, origin=self.current_pose[:3, 3]
        )
        
        # Update rendering
        self.vis.update_geometry(self.pcd)
        self.vis.update_geometry(self.coordinate_frame)
        self.vis.poll_events()
        self.vis.update_renderer()

    def save_map(self, filename="3d_map.ply"):
        """Save the generated point cloud to a PLY file"""
        if not self.map_points:
            print("No points to save")
            return
            
        # Create a point cloud from map points
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(np.array(self.map_points))
        
        # Save to file
        o3d.io.write_point_cloud(filename, pcd)
        print(f"Map saved to {filename}")

    def run(self):
        """Main processing loop"""
        try:
            print("Starting 3D mapping system...")
            print("Press Ctrl+C to stop and save the map")
            
            while True:
                # Get current time for delta calculation
                current_time = time.time()
                dt = current_time - self.last_update_time
                self.last_update_time = current_time
                
                # Read sensor data
                data_available = self.read_sensor_data()
                
                # Update angle (simulate sweep in simulation mode)
                self.current_angle = (self.current_angle + self.sweep_speed) % 180
                
                # Update pose estimation
                self.estimate_pose(dt)
                
                # Process current scan point
                point = self.scan_to_point(self.current_angle, self.sensor_data["Distance"])
                
                # Create keyframe if needed
                if point is not None and self.should_create_keyframe():
                    self.create_keyframe(point)
                
                # Update visualization
                self.update_visualization()
                
                # Print status occasionally (every 100 frames)
                if len(self.map_points) % 100 == 0 and len(self.map_points) > 0:
                    print(f"Map points: {len(self.map_points)}, Keyframes: {len(self.keyframes)}")
                    print(f"Current altitude: {self.sensor_data['Altitude']:.2f}m")
                
                # Small delay to prevent CPU hogging
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\nMapping stopped by user")
            self.save_map()
            if self.ser:
                self.ser.close()
            self.vis.destroy_window()
            print("Done!")

if __name__ == "__main__":
    mapping = LidarMappingSystem()
    mapping.run()