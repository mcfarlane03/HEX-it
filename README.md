# HEX-it: Drone-Based Remote Mapping and Sensing System

HEX-it is a drone-mounted embedded system designed for remote environment sensing and mapping. The system integrates LiDAR, IMU, thermal, and visual data to construct real-time occupancy maps and detect human presence in remote or hazardous environments.

## Features

- 📡 **Wireless Communication**: Utilizes two Heltec LoRa32 boards for long-range data transmission between sensor and receiver units.
- 🧭 **Mapping and Navigation**:
  - LiDAR and MPU6050 IMU data are used to create occupancy maps via MATLAB.
  - Employs MATLAB's LiDAR and Navigation Toolboxes.
- 🔥 **Fire Detection**:
  - BMP280 sensor monitors ambient temperature to detect potential fire events.
- 🧠 **Human Detection**:
  - ESP32-CAM runs TinyML models (TensorFlow Lite) for real-time object/person detection.
  - Communication between the ESP32-CAM and main sensor unit is handled via ESP-NOW.
- 🖥️ **Host Interface**:
  - MATLAB script reads serial data from the receiver LoRa32 and plots occupancy maps dynamically.

## Hardware Components

- Heltec LoRa32 (2x)
- ESP32-CAM
- LiDAR sensor
- MPU6050 (IMU)
- BMP280 (Temperature & Pressure)

## Software Stack

- Embedded C/C++ (Arduino Framework)
- MATLAB (LiDAR and Navigation Toolboxes)
- TensorFlow Lite for Microcontrollers (TinyML)
- ESP-NOW Protocol

## Use Case

This system is designed for real-time mapping and threat assessment in environments where direct human presence is not feasible, such as post-disaster zones or areas with fire risk.

## Getting Started

1. Upload Arduino sketches to each of the embedded devices.
2. Connect the receiver Heltec LoRa32 to a host computer via USB.
3. Run the MATLAB script to visualize incoming data.
4. Ensure ESP32-CAM is properly trained and loaded with TinyML detection models.

## License

MIT License
