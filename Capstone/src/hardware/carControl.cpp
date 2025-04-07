#include <Arduino.h>
#include <Wire.h>
#include <IRremote.hpp>
#include "MPU6050.h"
#include <TFLI2C.h>   // TFLuna-I2C Library v.0.1.1

// Motor Pins
#define MOTOR_SPEED_PIN_A 5  
#define MOTOR_SPEED_PIN_B 6  
#define MOTOR_DIR_PIN_A 7  
#define MOTOR_DIR_PIN_B 8  
#define MOTOR_STATE_PIN 3  

// IR Remote
#define RECV_PIN 9
#define IR_STOP 16712445       
#define IR_START 16736925     
#define Vext 36
#define SDA 33
#define SCL 34

// TF Mini I2C LiDAR
TFLI2C tflI2C;
int16_t tfDist;
int16_t tfAddr = TFL_DEF_ADR;

// Constants
#define OBSTACLE_DISTANCE_CM 35
#define GYRO_TOLERANCE 3.0
#define TURN_TOLERANCE 4.0
#define TURN_ANGLE 77
#define DEFAULT_SPEED 200

// Gyroscope
MPU6050 accelGyro;
int16_t gzo = 0;
float currentYaw = 0;
unsigned long lastUpdateTime = 0;

// IR
bool isStarted = false;  // flag for start/stop state

// Function Prototypes
void calibrateMPU6050();
void updateYaw();
void controlMotor(bool dirA, uint8_t speedA, bool dirB, uint8_t speedB, bool isEnable);
void stop();
void moveForwardGyro(int speed);
void turnRightGyro(int speed);
int readLiDARDistance();

void setup() {
    Serial.begin(9600);
    Wire.begin(SDA, SCL); 
    accelGyro.initialize();
    calibrateMPU6050();
    IrReceiver.begin(RECV_PIN, ENABLE_LED_FEEDBACK);
    pinMode(MOTOR_STATE_PIN, OUTPUT);
    pinMode(MOTOR_DIR_PIN_A, OUTPUT);
    pinMode(MOTOR_DIR_PIN_B, OUTPUT);
    Serial.println("Setup complete. Waiting for START...");
}

void calibrateMPU6050() {
    long sum = 0;
    for (int i = 0; i < 200; i++) {
        sum += accelGyro.getRotationZ();
        delay(10);
    }
    gzo = sum / 200;
}

void updateYaw() {
    unsigned long currentTime = millis();
    float deltaTime = (currentTime - lastUpdateTime) / 1000.0;
    lastUpdateTime = currentTime;
    if (deltaTime > 0.1) deltaTime = 0.1;

    int16_t gz = accelGyro.getRotationZ();
    float gyroz = -(gz - gzo) / 131.0;
    currentYaw += gyroz * deltaTime;

    if (currentYaw > 180) currentYaw -= 360;
    else if (currentYaw < -180) currentYaw += 360;
}

void controlMotor(bool dirA, uint8_t speedA, bool dirB, uint8_t speedB, bool isEnable) {
    digitalWrite(MOTOR_STATE_PIN, isEnable ? HIGH : LOW);
    digitalWrite(MOTOR_DIR_PIN_A, dirA);
    analogWrite(MOTOR_SPEED_PIN_A, speedA);
    digitalWrite(MOTOR_DIR_PIN_B, dirB);
    analogWrite(MOTOR_SPEED_PIN_B, speedB);
}

void stop() {
    Serial.println("STOP");
    controlMotor(false, 0, false, 0, false);
}

void moveForwardGyro(int speed) {
    float initialYaw = currentYaw;
    updateYaw();

    float yawError = currentYaw - initialYaw;
    int correction = abs(yawError) * 2;

    int leftSpeed = speed;
    int rightSpeed = speed;

    if (yawError > GYRO_TOLERANCE) {
        rightSpeed = max(speed - correction, speed / 2);
    } else if (yawError < -GYRO_TOLERANCE) {
        leftSpeed = max(speed - correction, speed / 2);
    }

    controlMotor(true, leftSpeed, true, rightSpeed, true);
}

void turnRightGyro(int speed) {
    float initialYaw = currentYaw;
    float targetYaw = initialYaw + TURN_ANGLE;
    if (targetYaw > 180) targetYaw -= 360;

    while (true) {
        updateYaw();
        float remaining = targetYaw - currentYaw;
        if (remaining > 180) remaining -= 360;
        else if (remaining < -180) remaining += 360;

        if (abs(remaining) <= TURN_TOLERANCE) {
            stop();
            break;
        }

        controlMotor(true, speed, false, speed, true);
    }
}

int readLiDARDistance() {
    if (tflI2C.getData(tfDist, tfAddr)) {
        return tfDist;
    } else {
        return -1;
    }
}

void loop() {
    updateYaw();
    
    // Check for IR input
    if (IrReceiver.decode()) {
        uint32_t receivedCode = IrReceiver.decodedIRData.decodedRawData;
    
        if (receivedCode == IR_STOP) {
            stop();
            isStarted = false;
            Serial.println("Stopped by remote.");
        } else if (receivedCode == IR_START) {
            isStarted = true;
            Serial.println("Started by remote.");
        }
        IrReceiver.resume();
    }

    // If not started, stay stopped
    if (!isStarted) {
        stop();
        delay(100);
        return;
    }

    // Main movement loop
    int dist = readLiDARDistance();
    if (dist > 0) {
        Serial.print("Distance: ");
        Serial.println(dist);
    }

    if (dist > 0 && dist <= OBSTACLE_DISTANCE_CM) {
        stop();
        delay(200);
        turnRightGyro(DEFAULT_SPEED);
        delay(200);
    } else {
        moveForwardGyro(DEFAULT_SPEED);
    }

    delay(50);  // smooth loop
}
