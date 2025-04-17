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
#include <ArduinoJson.h>

#include <RadioLib.h>
#include <esp_now.h>
#include <WiFi.h>

#define Vext 36
#define SDA 33
#define SCL 34

#define ALTITUDE 1013.25

#define DIO_1    14
#define NSS      8
#define RESET    12
#define BUSY     13

#define RXD2    3
#define TXD2    36

// #define LIDAR_FRONT_ADDR TFL_DEF_ADR  // Default address (0x10)
// #define LIDAR_BACK_ADDR  0x11         // Second LiDAR address
#define SERVO_PIN 45 

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance

TFLI2C tflI2C;

Servo sweepServo;

Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C

int16_t  tfDist;    // distance in centimeters
int16_t  tfAddr = TFL_DEF_ADR;  // Use this default I2C address

bool personDetected = false;
int txNumber = 0;
String personDetectionJSON = "";  // to store camera messages

// Servo sweep variables
int currentAngle = 0;
bool sweepingUp = true;
const int ANGLE_STEP = 6;  // Degrees to move per reading

// ESP-NOW configuration
typedef struct struct_message {
  bool detected;
} struct_message;

struct_message cameraData;

// Function to handle incoming data from ESP-NOW
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&cameraData, incomingData, sizeof(cameraData));
  personDetected = cameraData.detected;
  
  Serial.print("Person detection update: ");
  Serial.println(personDetected ? "DETECTED" : "NOT DETECTED");
}

// Function to update servo position
void updateServoPosition() {
  if (sweepingUp) {
      currentAngle += ANGLE_STEP;
      if (currentAngle >= 180) {
          sweepingUp = false;
          currentAngle = 180;
      }
  } else {
      currentAngle -= ANGLE_STEP;
      if (currentAngle <= 0) {
          sweepingUp = true;
          currentAngle = 0;
      }
  }
  sweepServo.write(currentAngle);
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

    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin();
    if (state == RADIOLIB_ERR_NONE) {
      Serial.println(F("success!"));
    } else {
      Serial.print(F("failed, code "));
      Serial.println(state);
      while (true) { delay(10); }
    }

    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW init failed");
        return;
    }
    esp_now_register_recv_cb(OnDataRecv);

    Serial.println("System ready - waiting for data...");

}

void loop(){

    personDetected = false;

    updateServoPosition(); // Move the servo to the next position

    tflI2C.getData( tfDist, tfAddr);
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // 3. JSON document

    JsonDocument doc;
    // doc["DistanceFront"] = distFront;
    // doc["DistanceBack"] = distBack;
    doc["Timestamp"] = millis();
    doc["Distance"] = tfDist;
    doc["Temp"] = bmp.readTemperature();
    doc["Pressure"] = bmp.readPressure();
    doc["Alti"] = bmp.readAltitude(ALTITUDE);
    doc["Accel_X"] = a.acceleration.x;
    doc["Accel_Y"] = a.acceleration.y;
    doc["Accel_Z"] = a.acceleration.z;
    doc["Rotat_X"] = g.gyro.x;
    doc["Rotat_Y"] = g.gyro.y;
    doc["Rotat_Z"] = g.gyro.z;
    doc["Angle"] = currentAngle; 
    doc["Sweep"] = sweepingUp ? "up" : "down";   
    doc["Human"] = personDetected;
     

   // 4. Send data over LoRa
    String jsonString;
    serializeJson(doc, jsonString);

    // serializeJson(doc, Serial);
    // Serial.println("");

    int state = radio.transmit(jsonString.c_str(), jsonString.length());

    if (state == RADIOLIB_ERR_NONE) {
      // the packet was successfully transmitted
      Serial.println(F("success!"));
  
      // print measured data rate
      Serial.print(F("[SX1262] Datarate:\t"));
      Serial.print(radio.getDataRate());
      Serial.println(F(" bps"));
  
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
  

    delay(500);
}