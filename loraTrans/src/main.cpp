/**
 * The code initializes various sensors and communication modules, reads sensor data, detects a person using a camera, and transmits sensor data and person detection status over LoRa communication.
 * 
 * @param mac The `mac` parameter in the `OnDataRecv` function represents the MAC address of the sender of the data received via ESP-NOW. It is a unique identifier assigned to each device for communication over a network.
 * @param incomingData The `incomingData` parameter in the `OnDataRecv` function is a pointer to the data received over the network. It is of type `const uint8_t*`, which means it is a pointer to an array of unsigned 8-bit integers (bytes) that represent the received data.
 * @param len The `len` parameter in the `OnDataRecv` function represents the length of the incoming data array that is being received. It indicates the size of the data being received from the sender device.
 */

#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
#include <TFLI2C.h>      // TFLuna-I2C Library v.0.1.1
#include <ESP32Servo.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <RadioLib.h>
#include <esp_now.h>
#include <WiFi.h>

// Pin and constant definitions
#define Vext 36
#define SDA 33
#define SCL 34

#define DIO_1    14
#define NSS      8
#define RESET    12
#define BUSY     13

#define SERVO_PIN 45 
#define ALTITUDE 1013.25

// Scanning parameters
#define ANGLE_STEP 5
#define ARRAY_SIZE 180  // Fixed array size (one per degree)
#define MAX_ANGLE 180   // Maximum servo angle
#define INVALID_DISTANCE 900  // Invalid distance value
#define MIN_PASSABLE_GAP 20   // Minimum passable gap in cm
#define MIN_ANGLE_CHANGE 3    // Minimum angle change to redirect (degrees)

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance

TFLI2C tflI2C;

Servo sweepServo;

Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C


// Global variables
int16_t tfDist; // distance in centimeters
int16_t tfAddr = TFL_DEF_ADR; // Use this default I2C address
int currentAngle = 0;
bool personDetected = false;
bool sweepInProgress = false;

// Add global variables for gap detection
int lastValidDistance = 0;
int dataIndex = 0;
bool retraceMode = false;

// ESP-NOW configuration
typedef struct struct_message {
  bool detected;
} struct_message;

struct_message cameraData;

typedef struct SensorData {
  uint32_t timestamp;
  int16_t distances[180];    
  float temperature;         
  float altitudes[180];      
  float accelX[180], accelY[180], accelZ[180];  
  float gyroX[180], gyroY[180], gyroZ[180];     
  int16_t angles[180];       // Servo angles
  bool humanDetected;
  int dataCount;            // Number of valid readings
  bool isPassable[180];     // Track passable points
} SensorData;

SensorData data;


// Function to handle incoming data from ESP-NOW
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&cameraData, incomingData, sizeof(cameraData));
  personDetected = cameraData.detected;
  
  Serial.print("Person detection update: ");
  Serial.println(personDetected ? "DETECTED" : "NOT DETECTED");
}

void setup(){
    
    //Turn Vext on to power Sensors
    pinMode(Vext,OUTPUT);
    digitalWrite(Vext, LOW);

    Serial.begin(115200);  // Initalize serial port
    Wire.begin(SDA, SCL);           // Initalize Wire library

    // Initialize servo
    sweepServo.attach(SERVO_PIN);
    sweepServo.write(0);  // Start at 0 degrees
    currentAngle = 0;

    if (!bmp.begin(0x76)) {
        Serial.println("Could not find a valid BMP280 sensor, check wiring!");
        while (1);
    }

    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
        Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
        Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
        Adafruit_BMP280::FILTER_X16,      /* Filtering. */
        Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
        while (1);
    }
    
     // Initialize LoRa
    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin();
    if (state == RADIOLIB_ERR_NONE) {
      Serial.println(F("success!"));
    } else {
      Serial.print(F("failed, code "));
      Serial.println(state);
      while (true) { delay(10); }
    }

    // Initialize ESP-NOW
    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW init failed");
        return;
    }
    esp_now_register_recv_cb(OnDataRecv);

    Serial.println("System ready - waiting for data...");

}

void loop() {
  
  personDetected = false;
  
  if (currentAngle == 0) {
    sweepInProgress = true;
    dataIndex = 0;
    data.temperature = bmp.readTemperature();
    lastValidDistance = 0;
  }

  // Take sensor readings
  tflI2C.getData(tfDist, tfAddr);
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Check for significant distance changes during sweep
  if (lastValidDistance > 0) {
    int distanceDiff = abs(tfDist - lastValidDistance);
    
    if (distanceDiff > MIN_PASSABLE_GAP) {
        // Calculate retracement angle between previous and current angle
        int previousAngle = currentAngle - ANGLE_STEP;
        float s = distanceDiff;
        float next_angle = s / tfDist;
        float deg_angle = next_angle * (180.0 / PI);
        int newAngle = previousAngle + (int)deg_angle;
        
        // Only retrace if angle difference is significant
        if (abs(newAngle - previousAngle) >= MIN_ANGLE_CHANGE) {
            // Store current position
            int returnAngle = currentAngle;
            
            // Move to calculated angle
            sweepServo.write(newAngle);
            delay(100);  // Allow servo to settle
            
            // Take new reading at calculated angle
            tflI2C.getData(tfDist, tfAddr);
            mpu.getEvent(&a, &g, &temp);
            
            // Store retracement data point
            if (dataIndex < ARRAY_SIZE) {
                data.distances[dataIndex] = tfDist;
                data.angles[dataIndex] = newAngle;
                data.altitudes[dataIndex] = bmp.readAltitude(ALTITUDE);
                data.accelX[dataIndex] = a.acceleration.x;
                data.accelY[dataIndex] = a.acceleration.y;
                data.accelZ[dataIndex] = a.acceleration.z;
                data.gyroX[dataIndex] = g.gyro.x;
                data.gyroY[dataIndex] = g.gyro.y;
                data.gyroZ[dataIndex] = g.gyro.z;
                data.isPassable[dataIndex] = (distanceDiff < MIN_PASSABLE_GAP);
                dataIndex++;
              }
                
              // Return to original sweep position
              currentAngle = returnAngle;
              sweepServo.write(returnAngle);
              delay(100);
          }
      }
  }
  
  // Store regular sweep reading
  if (dataIndex < ARRAY_SIZE) {
      data.distances[dataIndex] = tfDist;
      data.angles[dataIndex] = currentAngle;
      data.altitudes[dataIndex] = bmp.readAltitude(ALTITUDE);
      data.accelX[dataIndex] = a.acceleration.x;
      data.accelY[dataIndex] = a.acceleration.y;
      data.accelZ[dataIndex] = a.acceleration.z;
      data.gyroX[dataIndex] = g.gyro.x;
      data.gyroY[dataIndex] = g.gyro.y;
      data.gyroZ[dataIndex] = g.gyro.z;
      data.isPassable[dataIndex] = true;
      dataIndex++;
      lastValidDistance = tfDist;
  }
    // Continue normal sweep
    currentAngle += ANGLE_STEP;
    sweepServo.write(currentAngle);

    // Check if sweep complete or array full
    if (currentAngle >= MAX_ANGLE && sweepInProgress) {
        // Fill remaining array positions with invalid values if any
        while (dataIndex < ARRAY_SIZE) {
            data.distances[dataIndex] = INVALID_DISTANCE;
            data.angles[dataIndex] = currentAngle;
            data.isPassable[dataIndex] = false;
            dataIndex++;
        }

        data.dataCount = dataIndex;
        data.humanDetected = personDetected;
        data.timestamp = millis();

        // Transmit complete sweep data
        int state = radio.transmit((uint8_t*)&data, sizeof(data));
        
        
      if (state == RADIOLIB_ERR_NONE) {
          Serial.println(F("Sweep data transmitted successfully"));
          Serial.printf("Points collected: %d\n", data.dataCount);

      // print measured data rate
      Serial.print(F("[SX1262] Datarate:\t"));
      Serial.print(radio.getDataRate());
      Serial.println(F(" bps"));
  
  } else if (state == RADIOLIB_ERR_PACKET_TOO_LONG) {
      // the supplied packet was longer than 256 bytes
      Serial.println(F("too long!"));
  
  } else if (state == RADIOLIB_ERR_TX_TIMEOUT) {
      // timeout occurred while transmitting packet
      Serial.println(F("timeout!"));
  
  } else {
      // some other error occurred
      Serial.print(F("failed, code "));
      Serial.println(state);
  }
  
  // Reset for next sweep
  currentAngle = 0;
  sweepServo.write(0);
  sweepInProgress = false;
  dataIndex = 0;
  lastValidDistance = 0;

      
  delay(100);
  }

}