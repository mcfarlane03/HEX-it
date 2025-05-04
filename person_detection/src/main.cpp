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
#include <esp_now.h>
#include <WiFi.h>

// #define RXD2 3
// #define TXD2 40

// REPLACE WITH YOUR RECEIVER MAC Address
uint8_t broadcastAddress[] = {0x48, 0xCA, 0x43, 0xB7, 0xA7, 0x38};

// Structure to send detection data
typedef struct struct_message {
    bool detected;
  } struct_message;
  
  // Create a struct_message for detection data
  struct_message myData;
  
  esp_now_peer_info_t peerInfo;
  
  bool lastStatus = false;
  
  // callback when data is sent
  void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    Serial.print("\r\nLast Packet Send Status:\t");
    Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
  }
  

using eloq::camera;

using eloq::tinyml::zoo::personDetection;


void setup() {
    delay(3000);
    Serial.begin(115200);
    psramInit();
    //Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); // Initialize Serial2

    Serial.println("__PERSON DETECTION__");

    // Set device as a Wi-Fi Station
    WiFi.mode(WIFI_STA);

    // Init ESP-NOW
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // Register send callback
    esp_now_register_send_cb(OnDataSent);
  
    // Register peer
    memcpy(peerInfo.peer_addr, broadcastAddress, 6);
    peerInfo.channel = 0;  
    peerInfo.encrypt = false;
  
    // Add peer        
    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("Failed to add peer");
        return;
    }

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

        myData.detected = true;

        // Send message via ESP-NOW
        esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
        
        if (result == ESP_OK) {
            Serial.print("Detection status sent: ");
            Serial.println(currentStatus ? "PERSON DETECTED" : "NO PERSON");
        }
        else {
            Serial.println("Error sending the data");
        }
    }
    delay(100);
}
