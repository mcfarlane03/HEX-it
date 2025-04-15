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

#define ALTITUDE 1013.25

#define DIO_1    14
#define NSS      8
#define RESET    12
#define BUSY     13

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance

TFLI2C tflI2C;
Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C

int16_t  tfDist;    // distance in centimeters
int16_t  tfAddr = TFL_DEF_ADR;  // Use this default I2C address

int txNumber = 0;

void setup(){

    //Turn Vext on to power Sensors
    pinMode(Vext,OUTPUT);
    digitalWrite(Vext, LOW);

    Serial.begin(115200);  // Initalize serial port
    Wire.begin(SDA, SCL);           // Initalize Wire library

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


}

void loop(){

    // Serial.println("------------------TFLuna------------------");
  
    tflI2C.getData( tfDist, tfAddr);           

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    JsonDocument doc;
    doc["Distance"] = tfDist;
    doc["Temperature"] = bmp.readTemperature();
    doc["Pressure"] = bmp.readPressure();
    doc["Altitude"] = bmp.readAltitude(ALTITUDE);
    doc["Acceleration_X"] = a.acceleration.x;
    doc["Acceleration_Y"] = a.acceleration.y;
    doc["Acceleration_Z"] = a.acceleration.z;
    doc["Rotation_X"] = g.gyro.x;
    doc["Rotation_Y"] = g.gyro.y;
    doc["Rotation_Z"] = g.gyro.z;

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