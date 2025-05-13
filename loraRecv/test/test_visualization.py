import sys
import os
import numpy as np
import time
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loraRecv.src.matlab_int import RoomMapper

def run_visualization_test():
    mapper = RoomMapper(serial_port=None, baud_rate=115200)
    plt.ion()  # Enable interactive mode
    
    try:
        for i in range(30):  # 30 second test
            # Generate simulated room scan
            num_points = 72  # Every 5 degrees
            angles = np.linspace(0, 360, num_points)
            # Create circular room with noise
            base_distance = 1000
            noise = np.random.normal(0, 50, num_points)
            distances = base_distance + 100 * np.sin(np.radians(angles)) + noise
            
            test_data = {
                "timestamp": int(time.time() * 1000),
                "dataCount": num_points,
                "distances": distances.tolist(),
                "angles": angles.tolist(),
                "altitudes": [2000 + np.random.normal(0, 10) for _ in range(num_points)],
                "accelX": [0.1 * np.sin(i/10) for _ in range(num_points)],
                "accelY": [0.2 * np.cos(i/10) for _ in range(num_points)],
                "accelZ": [9.81 + np.random.normal(0, 0.01) for _ in range(num_points)],
                "gyroX": [0.01 * np.sin(i/5) for _ in range(num_points)],
                "gyroY": [0.01 * np.cos(i/5) for _ in range(num_points)],
                "gyroZ": [0.01 for _ in range(num_points)],
                "isPassable": [d > 500 for d in distances],
                "humanDetected": i % 5 == 0,  # Human detection every 5 seconds
                "temperature": 25.0 + np.random.normal(0, 0.1)
            }
            
            mapper.process_scan(test_data)
            plt.pause(1)
            
    except KeyboardInterrupt:
        print("\nVisualization test stopped")
    finally:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    run_visualization_test()