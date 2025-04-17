/**
 * Run person detection on ESP32 camera
 *  - Requires tflm_esp32 library
 *  - Requires EloquentEsp32Cam library
 *
 * Detections takes about 4-5 seconds per frame
 */
#include <Arduino.h>
#include <tflm_esp32.h>
#include <eloquent_tinyml.h>
#include <eloquent_tinyml/zoo/person_detection.h>
#include <eloquent_esp32cam.h>

#define RXD2 3
#define TXD2 40

using eloq::camera;

using eloq::tinyml::zoo::personDetection;

bool lastStatus = false;

void setup() {
    delay(3000);
    Serial.begin(115200);
    Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); // Initialize Serial2

    Serial.println("__PERSON DETECTION__");

    // camera settings
    camera.pinout.wroom_s3();
    camera.brownout.disable();
    // only works on 96x96 (yolo) grayscale images
    camera.resolution.yolo();
    camera.pixformat.gray();

    // init camera
    while (!camera.begin().isOk())
        Serial.println(camera.exception.toString());

    // init tf model
    while (!personDetection.begin().isOk())
        Serial.println(personDetection.exception.toString());

    Serial.println("Camera Ready");
    Serial.println("Waiting for person detection...");
}

void loop() {

    // capture picture
    if (!camera.capture().isOk()) {
        Serial.println(camera.exception.toString());
        return;
    }

    // run person detection
    if (!personDetection.run(camera).isOk()) {
        Serial.println(personDetection.exception.toString());
        return;
    }

    bool currentStatus = (bool)personDetection;
    unsigned long timestamp = millis();

    // a person has been detected!
    if (currentStatus && (currentStatus != lastStatus)) {
        lastStatus = currentStatus;

        // Send JSON result via Serial2
        Serial2.print("{\"detected\":1");
        Serial2.print(",\"personTimestamp\":");
        Serial2.print(timestamp);
        Serial2.println("}");

    //Debuging
        Serial.print("Person detected at ");
        Serial.println(timestamp);
    }else{
        lastStatus = currentStatus;
    }
}
