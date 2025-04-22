#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <vector>
#include <string>
#include <utility>

/*  The tank monitor consists in 3 contancts that are set to ground when the values are
*   normal (ie no detection of maxlevel, minlevel or leak), if there is one detection
*   the correspondant line got disconnected and its set to float (then you need to 
*   set the pins to be in pull up state to have a 1 value reading).
*   The microcontroller is a nodemcu amica, that can connects to wifi and runs a 
*   basic UDP server that answer to SCPI commands
*
*   This code can be used as a fairly easy template for a SCPI server.. you just need to 
*   define the pinouts, the functions to use and the correspondant SCPI commands
*   that triggers certain action.. the main loop can be let as it and should be ok.
*/


//This is a dirty replacement code for the non-working water sensor
//since I dont have the source code I am just guessing the behaviour
//of the previous system

//There was also a temperature mesurement.. 
//but I wont do it since it dont gave important info

//All this should be in a header..
const char* ssid {"FAKE-SSID"};    //put a valid WIFI SSID
const char* pass {"FAKE_PASS"};     //put here the correct password..

//pin assignation.. Check here bcs not all pins are available 
//https://randomnerdtutorials.com/esp8266-pinout-reference-gpios/
const int maxLevelSensor {D5};  //
const int minLevelSensor {D2};
const int leakSensor {D1};
const int ledPin {D4};

//ip address settings
IPAddress local_IP(10, 0, 33, 47);
// Set your Gateway IP address
IPAddress gateway(10, 0, 33, 1);

IPAddress subnet(255, 255, 255, 0);
//IPAddress primaryDNS(8, 8, 8, 8);   //optional
//IPAddress secondaryDNS(8, 8, 4, 4); //optional

//server hyperparameters
WiFiUDP udp;
char packetBuffer[255];
int packetSize {0};
int packetLen {0};
unsigned int localPort = 12334;


//functions to call 
int water_max_check(){
  Serial.println("reading max level");
  int data = digitalRead(maxLevelSensor);
  Serial.println(data);
  return data;
}

int water_min_check(){
  int data = digitalRead(minLevelSensor);
  return data;
}


int water_leak_check(){
  int data = digitalRead(leakSensor);
  return data;
}


//scpi cmds and the correspondent function
std::vector<std::pair<std::string_view, int(*)(void)>> cmds {
  {"APEX:SEQ:WATERTANK:MAX",water_max_check},
  {"APEX:SEQ:WATERTANK:MIN",water_min_check},
  {"APEX:SEQ:WATERTANK:LEAKSENSOR",water_leak_check}
};



void setup() {
  //setup Serial communication
  Serial.begin(115200);
  //pin modes
  pinMode(maxLevelSensor, INPUT_PULLUP);  
  pinMode(minLevelSensor, INPUT_PULLUP);
  pinMode(leakSensor, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); //just to know that the system is alive

  //set the static IP
  Serial.println("Configuring connection");

  if (!WiFi.config(local_IP, gateway, subnet)) {
    Serial.println("STA Failed to configure");
  }
  
  //connect to the wifi
  Serial.print("Trying to connect to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  Serial.println("Starting UDP server");
  udp.begin(localPort);

  Serial.print("Server started at ");
  Serial.print(WiFi.localIP());
  Serial.print(":");
  Serial.println(localPort);
}

void loop() {
  packetSize = udp.parsePacket();
  if(packetSize){
    Serial.print(" Received packet from : "); Serial.println(udp.remoteIP());
    Serial.print(" Size : "); Serial.println(packetSize);
    Serial.print(" Data : ");

    packetLen = udp.read(packetBuffer, 255);
    if (packetLen > 0) packetBuffer[packetLen - 1] = 0;    
    Serial.println(packetBuffer);

    //compare the received msg to excecute a command if it match
    for(auto& pair : cmds){
        if(strcmp(packetBuffer, pair.first.data())==0){
        Serial.print("Got ");
        Serial.println(pair.first.data());
        int read_value =pair.second();
        Serial.println(read_value);
        //send the data back to the client
        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write(std::to_string(read_value).data());
        udp.write("\r\n");
        udp.endPacket();
      }
    }
  }
}
