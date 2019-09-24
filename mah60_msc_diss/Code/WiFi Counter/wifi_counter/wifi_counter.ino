/**
   @author - mah60
   @version -
              0.1 - intial version of code, picks up packets and translates to
              mac address, RRSI and required data. - 20/07/2019;
              0.1.1 - completed documentation and comments - 21/07/2019;
              0.1.2 - Created method to apply a one-way hash on
              mac address found using the tracker. The hash has a keyword
              that is added to MD5 hashing to ensure it is harder to replicate
              the process. - 28/07/2019
              0.1.3 - code added to add timestamp to data collected - 05/08/2019
              0.1.4 - spit code into functions and created function and code
                      to upload data to database every x seconds - 06/08/2018;
              0.1.5 - documentation made and functions moved to header files
                      to reduce clutter on the main code written. - 06/08/2018;
              0.2.0 - functions added to record data to SD module, the pins used are
                      VCC -> VV , GND -> G, CS -> D8, MOSI -> D7, SCK -> D5, MOSO -> D6;

                      All strings variable types have been altered to only use char *,
                      This is due to the memory framentations that the String allocations
                      were causing. 

                      A filter system has also been attached to only search for mac addresses
                      in the provided csv file to that function.

*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
//#include <Crypto.h>
#include <MD5.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <stdio.h>
//#include <string.h>
#include <SPI.h>
#include <SD.h>

//#define Debug
#define MaxChannel 11
#define ChannelTime  1 // time in millieseconds 

char trackerMacAddress[50]; // this device personal mac address
char startDateTime[50]; // "year-month-day-hour-min-sec"
float startMillis; // run time when application time and wifi is set up in seconds
bool isWifi;
float previousTransmissionMillis = 0; // last time data was sent

// wifi username and password
//const char *ssid     = "VodafoneConnect22794042";
//const char *password = "5jh5xjz7b9zw2h9";
const char *ssid     = "BTHub6-Q3QS";
const char *password = "UxGrfcU96dgP";

char filteredMacAddress[902]; // can hold 50 macaddresses each with 18 characters
int commaLoc[51];  // references the start and end location of each mac address
int filterCount = 0; // number of filters in the file

// Define NTP Client to get time
const long utcOffsetInSeconds = 3600;
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

#include "generalFun.h"
#include "SdCard.h"
#include "GetCurrentDT.h"
#include "wifiAndPromiscuousMode.h"
#include "sendRecordedData.h"


void setup()
{
  // Serial setup
  Serial.begin(115200);
  delay(10);
  wifi_set_channel(9);

  Serial.println("Setting Up wifi tracker");

  startMillis = (float)millis() / 1000; // get start millis
  // turn on wifi
  connectToWifi();

  // start up sd card connection
  setupSD();
  char * filtLoc = "filteredMacAddresses.csv";
  getFilters(filtLoc);

  // if conneceted to wifi get start time
  timeClient.begin();

  timeClient.update();
  // get start date time
  getTimeStamp(startDateTime);
  Serial.println(startDateTime);

  startMillis = (float)millis() / 1000; // get start millis

  // get mac adress for this device and hash it
  byte mac[6];
  WiFi.macAddress(mac);
  for ( int i = 0; i < sizeof(mac); i++) {
    char macPart[20];
    decToHex(mac[i], macPart);
    strcat(trackerMacAddress, macPart);
    if (i != 5 ) {
      strcat(trackerMacAddress, ":");
    }
  }

  Serial.println(trackerMacAddress);


  // turn on promiscuous mode
  enablePromiscuousMode();


}


void loop() {
  // put your main code here, to run repeatedly:
  // loop through each channel for the wifi

  for (int ch = 1; ch <= MaxChannel; ch++) {
    wifi_set_channel(ch); // change channel
    // wait for x amount of time -  ChannelTime - seconds
    for (int t = 0; t < ChannelTime * 100; t++ ) {
      delay(10);
    }
  }
  #ifdef Debug
  // connect to wifi to send data to database
  int transmitTime = 1 * 60; // send data every x seconds
  // is it time to transmit
  if (getRunTime() > (previousTransmissionMillis + transmitTime)) {
    previousTransmissionMillis = getRunTime();  // set previous sent timer
    sendRecords(); // send recorded data
  }
  #endif
}
