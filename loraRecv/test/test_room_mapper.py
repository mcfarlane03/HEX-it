import unittest
import sys
import os
import json
import numpy as np
import time
import matplotlib.pyplot as plt
from unittest.mock import Mock, patch

# Add parent directory to path to import RoomMapper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.serialReader import RoomMapper

class TestRoomMapper(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Disable plotting for normal tests
        plt.ioff()
    
    def setUp(self):
        # Mock serial port for testing
        with patch('serial.Serial') as mock_serial:
            self.mapper = RoomMapper(serial_port='MOCK', baud_rate=115200)
            self.mock_serial = mock_serial
    
    def generate_test_data(self, num_points=1, with_human=False):
        return {
            "timestamp": int(time.time() * 1000),
            "dataCount": num_points,
            "distances": [1000] * num_points,
            "angles": list(np.linspace(0, 360, num_points)),
            "altitudes": [2000] * num_points,
            "accelX": [0.1] * num_points,
            "accelY": [0.2] * num_points,
            "accelZ": [9.81] * num_points,
            "gyroX": [0.01] * num_points,
            "gyroY": [0.02] * num_points,
            "gyroZ": [0.03] * num_points,
            "isPassable": [True] * num_points,
            "humanDetected": with_human,
            "temperature": 25.0
        }

    def test_data_processing(self):
        test_data = self.generate_test_data()
        self.mapper.process_scan(test_data)
        csv_file = os.path.join(self.mapper.data_dir, 'scan_data.csv')
        self.assertTrue(os.path.exists(csv_file))

    def test_coordinate_conversion(self):
        test_data = self.generate_test_data(num_points=1)
        test_data["angles"] = [45]
        
        expected_x = 1000 * np.cos(np.radians(45))
        expected_y = 1000 * np.sin(np.radians(45))
        
        self.mapper.process_scan(test_data)
        self.assertAlmostEqual(expected_x, 707.106, places=2)
        self.assertAlmostEqual(expected_y, 707.106, places=2)

    def test_human_detection(self):
        test_data = self.generate_test_data(with_human=True)
        self.mapper.process_scan(test_data)
        
        csv_file = os.path.join(self.mapper.data_dir, 'scan_data.csv')
        with open(csv_file, 'r') as f:
            last_line = f.readlines()[-1]
            self.assertIn('True', last_line)

    def tearDown(self):
        if hasattr(self.mapper, 'data_dir') and os.path.exists(self.mapper.data_dir):
            import shutil
            shutil.rmtree(self.mapper.data_dir)
        plt.close('all')

if __name__ == '__main__':
    unittest.main()