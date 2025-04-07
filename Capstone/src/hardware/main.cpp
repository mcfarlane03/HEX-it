#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
#include <TFLI2C.h>      // TFLuna-I2C Library v.0.1.1
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>

#define Vext 36
#define SDA 33
#define SCL 34

#define ALTITUDE 1013.25

TFLI2C tflI2C;
Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C

int16_t  tfDist;    // distance in centimeters
int16_t  tfAddr = TFL_DEF_ADR;  // Use this default I2C address

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


}

void loop(){

    // Serial.println("------------------TFLuna------------------");
  
    if( tflI2C.getData( tfDist, tfAddr)) // If read okay...
    {
        // Serial.print("Dist: ");
        // Serial.print(tfDist);          // print the data...
        // Serial.println(" cm");
    }
    else{ 
        
        // tflI2C.printStatus(); // print the status of the last operation
        // Serial.println("");

    };           

    // Serial.println("------------------BMP280------------------");

    // Serial.print("Temperature = ");
    // Serial.print(bmp.readTemperature());
    // Serial.println(" *C");

    // Serial.print("Pressure = ");
    // Serial.print(bmp.readPressure());
    // Serial.println(" Pa");

    // Serial.print("Altitude = ");
    // Serial.print(bmp.readAltitude(ALTITUDE)); // this should be adjusted to your local forcase
    // Serial.println(" m");

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Serial.println("------------------MPU6050------------------");

    // Serial.print("Acceleration X: "); Serial.print(a.acceleration.x); Serial.print(" m/s^2");
    // Serial.print("\tY: "); Serial.print(a.acceleration.y); Serial.print(" m/s^2");
    // Serial.print("\tZ: "); Serial.print(a.acceleration.z); Serial.println(" m/s^2");

    // Serial.print("Rotation X: "); Serial.print(g.gyro.x); Serial.print(" rad/s");
    // Serial.print("\tY: "); Serial.print(g.gyro.y); Serial.print(" rad/s");
    // Serial.print("\tZ: "); Serial.print(g.gyro.z); Serial.println(" rad/s");


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

    serializeJson(doc, Serial);
    Serial.println("");


    delay(500);
}