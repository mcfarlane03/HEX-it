#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
#include <TFLI2C.h>      // TFLuna-I2C Library v.0.1.1
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>

#include <RadioLib.h>
 #include <esp_now.h>
 #include <WiFi.h>
  #include <ESP32Servo.h>

#define Vext 36
#define SDA 33
#define SCL 34

#define ALTITUDE 1013.25

#define DIO_1    14
#define NSS      8
#define RESET    12
#define BUSY     13

#define SERVO_PIN 45 

 // Scanning parameters
 #define ANGLE_STEP 5
 #define ARRAY_SIZE 45  
 #define MAX_ANGLE 180   // Maximum servo angle
 #define INVALID_DISTANCE 900  // Invalid distance value
 #define MIN_PASSABLE_GAP 20   // Minimum passable gap in cm
 #define MIN_ANGLE_CHANGE 3    // Minimum angle change to redirect (degrees)
 

struct sensor_data {
  int8_t device_id; // Device ID
  int16_t range[45]; // Distance in centimeters
  int16_t angle[45]; // Angle in degrees
  float temperature; // Temperature in degrees Celsius
  int32_t timestamp; // Timestamp in milliseconds
  bool personDetectedFlag; // Person detected flag
} typedef sensor_data; // Define the data structure 

union tx_packet{
  uint8_t buffer[sizeof(sensor_data)]; // Buffer to hold the data
  sensor_data data; // Data to be transmitted
};

// ESP-NOW configuration
typedef struct struct_message {
  bool detected;
} struct_message;

struct_message cameraData;

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance
tx_packet packet; // Create packet instance


TFLI2C tflI2C;
Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C
Servo sweepServo; // Servo object

int16_t  tfDist;    // distance in centimeters
int16_t  tfAddr = TFL_DEF_ADR;  // Use this default I2C address

int currentAngle = 0;
bool personDetected = false;
bool sweepInProgress = false;
int txNumber = 0;
int dataIndex = 0;          
int lastValidDistance = 0 ;  

uint32_t currentTime = 0;

void initializeSensors();
void initializeRadio();
void initializeEspNow();
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len);
float calculateRelativeAngle(float gyroZ, int servoAngle);

void setup(){

  Serial.begin(115200);

  initializeSensors(); // Initialize sensors
  initializeRadio();   // Initialize radio
  initializeEspNow(); // Initialize ESP-NOW
  
  packet.data.device_id = 1;

}

void loop(){
  //personDetected = false;
  
  if (currentAngle == 0) {
    sweepInProgress = true;
    dataIndex = 0;
    packet.data.temperature = bmp.readTemperature();
    lastValidDistance = 0;
    
  }


  // Serial.println("------------------TFLuna------------------");

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
        delay(50);  // Allow servo to settle

        // Take new reading at calculated angle
        tflI2C.getData(tfDist, tfAddr);
        mpu.getEvent(&a, &g, &temp);
        
        // Store retracement data point if we have space
        if (dataIndex < ARRAY_SIZE) {
          packet.data.range[dataIndex] = tfDist;
          packet.data.angle[dataIndex] = calculateRelativeAngle(g.gyro.z,newAngle);

          dataIndex++;
        }
        // Return to original sweep position
        currentAngle = returnAngle;
        sweepServo.write(returnAngle);
        delay(100);
    }
  }
} 
      // Move servo to next angle regular sweep
      if (dataIndex < ARRAY_SIZE) {
          packet.data.range[dataIndex] = tfDist;
          packet.data.angle[dataIndex] = calculateRelativeAngle(g.gyro.z,currentAngle);
          lastValidDistance = tfDist;
          dataIndex++;
        }
        currentAngle += ANGLE_STEP;
        sweepServo.write(currentAngle);
        
      // Check if sweep complete or array full
     if (currentAngle >= MAX_ANGLE && sweepInProgress) {
      while (dataIndex < ARRAY_SIZE) {
        packet.data.range[dataIndex] = INVALID_DISTANCE;
        packet.data.angle[dataIndex] = calculateRelativeAngle(g.gyro.z,currentAngle);
        dataIndex++;
        lastValidDistance = tfDist;
      }
        packet.data.personDetectedFlag = personDetected;
        packet.data.timestamp = millis();
  
  int state = radio.transmit(packet.buffer, sizeof(packet.buffer)); // Transmit the packet

  if (state == RADIOLIB_ERR_NONE) {
    // the packet was successfully transmitted
    Serial.println(F("Transmission successful!"));
    
    // Print some info about what we sent (for debugging)
    Serial.print("Device ID: ");
    Serial.println(packet.data.device_id);
    Serial.println("\nDistances [cm]:");
    for (int i = 0; i < 45; i += 1) { // Print every 5th value
      Serial.print(packet.data.range[i]); Serial.print(" ");
    }
    
    Serial.println("\nAngles [deg]:");
    for (int i = 0; i < 45; i+= 1) {
      Serial.print(packet.data.angle[i]); Serial.print(" ");
    }
    Serial.print("\nTemperature: ");
    Serial.print(packet.data.temperature);
    Serial.println(" °C");
    Serial.print("\nTimestamp: ");
    Serial.println(packet.data.timestamp);



  } else if (state == RADIOLIB_ERR_PACKET_TOO_LONG) {
    // the supplied packet was longer than 256 bytes
    Serial.println(F("too long!"));

  } else if (state == RADIOLIB_ERR_TX_TIMEOUT) {
    // timeout occured while transmitting packet
    Serial.println(F("timeout!"));

  } else {
    // some other error occurred
    Serial.print(F("failed, code "));
    Serial.println(state);

  }

  while (millis() - currentTime < 500) {}
  currentTime = millis(); // Update current time

  sweepServo.write(0);
  personDetected = false;
  sweepInProgress = false;
  currentAngle = 0;
  dataIndex = 0;
  lastValidDistance = 0;

  memset(&packet.data, 0, sizeof(packet.data));
  packet.data.device_id = 1; // Restore device ID
  
}
}


void initializeSensors() {
  //Turn Vext on to power Sensors
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, LOW);

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

}

void initializeRadio(){

  Serial.print(F("[SX1262] Initializing ... "));
  int state = radio.begin();
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("success!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true) { delay(10); }
  }

}

void initializeEspNow(){
   // Initialize ESP-NOW
   WiFi.mode(WIFI_STA);
   if (esp_now_init() != ESP_OK) {
       Serial.println("ESP-NOW init failed");
       return;
   }
   esp_now_register_recv_cb(OnDataRecv);

}

 // Function to handle incoming data from ESP-NOW
 void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&cameraData, incomingData, sizeof(cameraData));
  personDetected = cameraData.detected;
  
  Serial.print("Person detection update: ");
  Serial.println(personDetected ? "DETECTED" : "NOT DETECTED");
}

// Function to calculate the relative angle based on gyro data and servo angle
float calculateRelativeAngle(float gyroZ, int servoAngle) {
  static float integratedGyroAngle = 0;
  static unsigned long lastTime = 0;
  
  unsigned long currentTime = millis();
  float deltaTime = (currentTime - lastTime) / 1000.0;
  lastTime = currentTime;
  
  if (deltaTime < 1.0) {
      integratedGyroAngle += gyroZ * RAD_TO_DEG * deltaTime;
  }
  
  float relativeAngle = servoAngle - integratedGyroAngle;
  while(relativeAngle > 180) relativeAngle -= 360;
  while(relativeAngle < -180) relativeAngle += 360;
  
  return relativeAngle;
}