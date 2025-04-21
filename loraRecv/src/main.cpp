#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
#include <TFLI2C.h>      // TFLuna-I2C Library v.0.1.1
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>
#include <RadioLib.h>





#define Vext 36
#define SDA 33
#define SCL 34

#define DIO_0    26
#define DIO_1    14
#define NSS      8
#define RESET    12
#define BUSY     13

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance

// Define the struct
typedef struct SensorData {
  uint32_t timestamp;
  int16_t distances[180];    
  float temperature;         
  float altitudes[180];      
  float accelX[180], accelY[180], accelZ[180];  
  float gyroX[180], gyroY[180], gyroZ[180];     
  int16_t angles[180];       
  bool humanDetected;
  int dataCount;            
  bool isPassable[180];     
} SensorData;

int count = 0;
#define INVALID_DISTANCE -1
volatile bool receivedFlag = false;

// this function is called when a complete packet
// is received by the module
// IMPORTANT: this function MUST be 'void' type
//            and MUST NOT have any arguments!
#if defined(ESP8266) || defined(ESP32)
  ICACHE_RAM_ATTR
#endif
void setFlag(void) {
  // we got a packet, set the flag
  receivedFlag = true;
}

void setup(){

    Serial.begin(115200);  // Initalize serial port
    Wire.begin(SDA, SCL);           // Initalize Wire library

    //Turn Vext on to power Sensors
    pinMode(Vext,OUTPUT);
    digitalWrite(Vext, LOW);

    Serial.print(F("[SX1262] Initializing ... "));
    int state = radio.begin();
    if (state == RADIOLIB_ERR_NONE) {
        Serial.println(F("success!"));
    } 
    
    else {
        Serial.print(F("failed, code "));
        Serial.println(state);
        while (true) { delay(10); }
    }

    radio.setPacketReceivedAction(setFlag);

  // start listening for LoRa packets
  Serial.print(F("[SX1262] Starting to listen ... "));
  state = radio.startReceive();
  if (state == RADIOLIB_ERR_NONE) {
    Serial.println(F("success!"));
  } else {
    Serial.print(F("failed, code "));
    Serial.println(state);
    while (true) { delay(10); }
  }
}

void loop() {
  if (receivedFlag) {
    receivedFlag = false;

    SensorData receivedData;
    int state = radio.readData((byte *)&receivedData, sizeof(SensorData));

    if (state == RADIOLIB_ERR_NONE) {
      // Successfully received struct
      Serial.println(F("[Receiver] Received sweep data:"));
      Serial.printf("Timestamp: %lu ms\n", receivedData.timestamp);
      Serial.printf("Temperature: %.2f °C\n", receivedData.temperature);
      Serial.printf("Valid data points: %d\n", receivedData.dataCount);
      Serial.printf("Human detected: %s\n", receivedData.humanDetected ? "YES" : "NO");

      // Print all valid measurements
      for (int i = 0; i < receivedData.dataCount; i++) {
          if (receivedData.distances[i] != INVALID_DISTANCE) {
              Serial.printf("\nPoint %d:\n", i);
              Serial.printf("  Angle: %d°\n", receivedData.angles[i]);
              Serial.printf("  Distance: %d cm\n", receivedData.distances[i]);
              Serial.printf("  Altitude: %.2f m\n", receivedData.altitudes[i]);
              Serial.printf("  Acceleration (x,y,z): %.2f, %.2f, %.2f\n", 
                  receivedData.accelX[i], 
                  receivedData.accelY[i], 
                  receivedData.accelZ[i]);
              Serial.printf("  Gyro (x,y,z): %.2f, %.2f, %.2f\n",
                  receivedData.gyroX[i], 
                  receivedData.gyroY[i], 
                  receivedData.gyroZ[i]);
              Serial.printf("  Passable: %s\n", 
                  receivedData.isPassable[i] ? "YES" : "NO");
          }
      }

    } else {
      Serial.print(F("Receive failed, code "));
      Serial.println(state);
    }

    radio.startReceive();  // Restart receive mode
    delay(10);
  }
}
