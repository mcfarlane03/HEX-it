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

union rx_packet {
  uint8_t buffer[sizeof(sensor_data)];
  sensor_data data;
};

SX1262 radio = new Module(NSS, DIO_1, RESET, BUSY); // Create radio instance


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

void loop(){

  if(receivedFlag) {
    // reset flag
    receivedFlag = false;

    // you can read received data as an Arduino String
    rx_packet packet;
    int state = radio.readData(packet.buffer, sizeof(packet.buffer));

    if (state == RADIOLIB_ERR_NONE) {
      // // packet was successfully received
      // Serial.println(F("[SX1262] Received packet!"));

      // // print data of the packet
      // Serial.print(F("[SX1262] Data:\t\t"));
      // Serial.println(str);

      Serial.print("Received from device: ");
      Serial.println(packet.data.device_id);


      
      // Print sample data
      for(int i = 0; i < 45; i += 5) {
        Serial.print(packet.data.range[i]); Serial.print("cm @ ");
        Serial.print(packet.data.angle[i]); Serial.println("°");
      }

      Serial.print("Temperature: ");
      Serial.print(packet.data.temperature);
      Serial.println(" °C");
      Serial.print("Timestamp: ");
      Serial.println(packet.data.timestamp);
      Serial.print("Person detected: ");
      Serial.println(packet.data.personDetectedFlag ? "Yes" : "No");
      Serial.println("------------------End of packet------------------");
     }

     else 
     {
        // some other error occurred
        Serial.print(F("failed, code "));
        Serial.println(state);
  
    }
  }
}
j