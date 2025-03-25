#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
#include <TFLI2C.h>      // TFLuna-I2C Library v.0.1.1
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_MPU6050.h>
#include <ArduinoJson.h>
#include <MadgwickAHRS.h> // Madgwick filter

#define Vext 36
#define SDA 33
#define SCL 34
#define ALTITUDE 1013.25
#define UPDATE_RATE_HZ 100
#define UPDATE_INTERVAL_MICROS (1000000 / UPDATE_RATE_HZ)

TFLI2C tflI2C;
Adafruit_BMP280 bmp; // I2C
Adafruit_MPU6050 mpu; // I2C
Madgwick filter;

int16_t  tfDist;    // distance in centimeters
int16_t  tfAddr = TFL_DEF_ADR;  // Use this default I2C address

// Timing Variables
unsigned long lastMicros = 0;
unsigned long lastUpdateMicros = 0;
float currentYaw = 0, currentPitch = 0, currentRoll = 0;

// Calibration Variables
struct CalibrationData {
    float gyroOffsetX = 0;
    float gyroOffsetY = 0;
    float gyroOffsetZ = 0;
    float accelOffsetX = 0;
    float accelOffsetY = 0;
    float accelOffsetZ = 0;
} calibrationData;

void performCalibration() {
    const int calibrationSamples = 1000;
    
    Serial.println("Starting sensor calibration...");

    calibrationData = CalibrationData(); // Reset calibration data
    
    for (int i = 0; i < calibrationSamples; i++) {
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);

        // Accumulate gyroscope and accelerator offsets
        calibrationData.gyroOffsetX += g.gyro.x;
        calibrationData.gyroOffsetY += g.gyro.y;
        calibrationData.gyroOffsetZ += g.gyro.z;
        
        calibrationData.accelOffsetX += a.acceleration.x;
        calibrationData.accelOffsetY += a.acceleration.y;
        calibrationData.accelOffsetZ += a.acceleration.z;
        
        delay(1);
    }
    
    // Calculate average offsets
    calibrationData.gyroOffsetX /= calibrationSamples;
    calibrationData.gyroOffsetY /= calibrationSamples;
    calibrationData.gyroOffsetZ /= calibrationSamples;
    
    calibrationData.accelOffsetX /= calibrationSamples;
    calibrationData.accelOffsetY /= calibrationSamples;
    calibrationData.accelOffsetZ -= 9.81;

    Serial.println("Calibration Complete.");
    Serial.print("Gyro Offsets - X: "); Serial.print(calibrationData.gyroOffsetX);
    Serial.print(" Y: "); Serial.print(calibrationData.gyroOffsetY);
    Serial.print(" Z: "); Serial.println(calibrationData.gyroOffsetZ);
}

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
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
        while (1);
    }
     // ConfigureBMP280
    bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,     /* Operating Mode. */
        Adafruit_BMP280::SAMPLING_X2,     /* Temp. oversampling */
        Adafruit_BMP280::SAMPLING_X16,    /* Pressure oversampling */
        Adafruit_BMP280::FILTER_X16,      /* Filtering. */
        Adafruit_BMP280::STANDBY_MS_500); /* Standby time. */

   // Configure MPU6050
   mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
   mpu.setGyroRange(MPU6050_RANGE_500_DEG);
   mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

   filter.begin(100); //Initialize Madgwick Filter to 100 Hz sample rate
   performCalibration();
   lastMicros = micros();


}

void loop(){

    unsigned long currentMicros = micros();
    float deltaTime = (currentMicros - lastMicros) / 1000000.0f;
    lastMicros = currentMicros;

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // if( tflI2C.getData( tfDist, tfAddr)) // If read okay...
    // {
         // Serial.print("Dist: ");
         // Serial.print(tfDist);          // print the data...
         // Serial.println(" cm");
    // }
    // else{ 
        
        // tflI2C.printStatus(); // print the status of the last operation
         // Serial.println("");

    // };           

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

    // Serial.println("------------------MPU6050------------------");

    // Serial.print("Acceleration X: "); Serial.print(a.acceleration.x); Serial.print(" m/s^2");
    // Serial.print("\tY: "); Serial.print(a.acceleration.y); Serial.print(" m/s^2");
    // Serial.print("\tZ: "); Serial.print(a.acceleration.z); Serial.println(" m/s^2");

    // Serial.print("Rotation X: "); Serial.print(g.gyro.x); Serial.print(" rad/s");
    // Serial.print("\tY: "); Serial.print(g.gyro.y); Serial.print(" rad/s");
    // Serial.print("\tZ: "); Serial.print(g.gyro.z); Serial.println(" rad/s");

    g.gyro.x -= calibrationData.gyroOffsetX;
    g.gyro.y -= calibrationData.gyroOffsetY;
    g.gyro.z -= calibrationData.gyroOffsetZ;
    
    a.acceleration.x -= calibrationData.accelOffsetX;
    a.acceleration.y -= calibrationData.accelOffsetY;
    a.acceleration.z -= calibrationData.accelOffsetZ;

    filter.update(g.gyro.x, g.gyro.y, g.gyro.z, a.acceleration.x, a.acceleration.y, a.acceleration.z, 0.0f, 0.0f, 0.0f);
    
    currentYaw = filter.getYaw();
    currentPitch = filter.getPitch();
    currentRoll = filter.getRoll();

    bool isDistanceValid = tflI2C.getData(tfDist, tfAddr);



    JsonDocument doc;
    doc["Timestamp"] = currentMicros;
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
    doc["Yaw"] = currentYaw;
    doc["Pitch"] = currentPitch;
    doc["Roll"] = currentRoll;

    serializeJson(doc, Serial);
    Serial.println("");


    delay(500);
}