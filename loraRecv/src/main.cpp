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
  int16_t distance;
  float temperature;
  float altitude;
  float accel_x;
  float accel_y;
  float accel_z;
  float rotat_x;
  float rotat_y;
  float rotat_z;
  int16_t angle;
  bool sweep;
  bool human;
} SensorData;

int count = 0;

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

    SensorData data;
    int state = radio.readData((byte *)&data, sizeof(SensorData));

    if (state == RADIOLIB_ERR_NONE) {
      // Successfully received struct
      Serial.println(F("[Receiver] Received sensor data:"));

      Serial.printf("Timestamp: %lu ms\n", data.timestamp);
      Serial.printf("Distance: %d cm\n", data.distance);
      Serial.printf("Temperature: %.2f °C\n", data.temperature);
      Serial.printf("Altitude: %.2f m\n", data.altitude);

      Serial.printf("Accel X: %.2f m/s²\n", data.accel_x);
      Serial.printf("Accel Y: %.2f m/s²\n", data.accel_y);
      Serial.printf("Accel Z: %.2f m/s²\n", data.accel_z);

      Serial.printf("Gyro X: %.2f rad/s\n", data.rotat_x);
      Serial.printf("Gyro Y: %.2f rad/s\n", data.rotat_y);
      Serial.printf("Gyro Z: %.2f rad/s\n", data.rotat_z);

      Serial.printf("Servo Angle: %d°\n", data.angle);
      Serial.printf("Sweeping %s\n", data.sweep ? "up" : "down");
      Serial.printf("Person Detected: %s\n", data.human ? "YES" : "NO");

    } else {
      Serial.print(F("Receive failed, code "));
      Serial.println(state);
    }

    radio.startReceive();  // Restart receive mode
    delay(10);
  }
}
