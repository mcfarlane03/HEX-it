#include <Arduino.h>
#include <Wire.h>        // Instantiate the Wire library
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


struct sensor_data {
  int8_t device_id;
  int16_t range[45];
  int16_t angle[45];
  float temperature;
  int32_t timestamp;
  bool personDetectedFlag;
};

struct imu_data {
  int8_t device_id;
  float gyro_z;
  float accel_x;
  float accel_y;
};

union sensor_packet {
  uint8_t buffer[sizeof(sensor_data)];
  sensor_data data;
};

union imu_packet {
  uint8_t buffer[sizeof(imu_data)];
  imu_data data;
};

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance

sensor_packet packet1;
imu_packet packet2;

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
    // Reset flag
    receivedFlag = false;

    // Read the first packet
    int state1 = radio.readData(packet1.buffer, sizeof(packet1.buffer));

    if (state1 == RADIOLIB_ERR_NONE && packet1.data.device_id == 1) {
      // Wait for the second packet
      while (!receivedFlag) {
        delay(10);
      }

      // Reset flag
      receivedFlag = false;

      // Read the second packet
      int state2 = radio.readData(packet2.buffer, sizeof(packet2.buffer));

      if (state2 == RADIOLIB_ERR_NONE && packet2.data.device_id == 2) {
        // Combine data into a JSON object
        StaticJsonDocument<1024> doc;
        JsonArray range = doc.createNestedArray("ranges");
        JsonArray angle = doc.createNestedArray("angles");

        for (int i = 0; i < 45; i++) {
          range.add(packet1.data.range[i]);
          angle.add(packet1.data.angle[i]);
        }

        doc["device_id_1"] = packet1.data.device_id;
        doc["temperature"] = packet1.data.temperature;
        doc["timestamp"] = packet1.data.timestamp;
        doc["personDetectedFlag"] = packet1.data.personDetectedFlag;

        doc["device_id_2"] = packet2.data.device_id;
        doc["rotation_z"] = packet2.data.gyro_z;
        doc["accel_x"] = packet2.data.accel_x;
        doc["accel_y"] = packet2.data.accel_y;

        // Serialize JSON and send over serial
        serializeJson(doc, Serial);
        Serial.println();
      } else {
        // Drop both packets if the second packet is invalid or not ID2
        Serial.println("Second packet invalid or not ID2. Dropping both packets.");
      }
    } else {
      // Drop the first packet if it is not ID1
      Serial.println("First packet invalid or not ID1. Dropping packet.");
    }
  }
}
