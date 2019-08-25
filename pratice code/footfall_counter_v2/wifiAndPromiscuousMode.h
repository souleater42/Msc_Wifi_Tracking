#ifndef wifiAndPromiscuousMode.h
#define wifiAndPromiscuousMode.h

#include "PacketTypes.h"

// wifi ------------------------------------------------------------


/**
   @summary - connect the device to the wifi.
   @description - will connect this device to the internet
                  and the wifihub name and password used will be
                  defined in; ssid & password variables.
   @author - mah60
   @params - None
   @return - None
*/
void connectToWifi() {

  wifi_promiscuous_enable(0);

  WiFi.begin(ssid, password);
  int waitTime = 20; // time to wait until declare unable to connect in seconds
  float addWaitTime = getRunTime();
  while ( WiFi.status() != WL_CONNECTED ) {
    delay (500);
    Serial.print(".");
    // if wifi hasn't connected in 'waitTime' continue without wifi
    if (getRunTime() > (addWaitTime + waitTime)) {
      isWifi = false;
      Serial.println("");
      Serial.println("cannot connect to wifi");
      break;
    } else { // declare connection to wifi
      isWifi = true;
    }
  }

  if (isWifi) {
    Serial.println("");
    Serial.println("connected to wifi");
  }
  // Wifi setup
  wifi_set_opmode(STATION_MODE);

}



// promiscuous mode ------------------------------------------------
/**
   @summary - applies MD5 hash to string given.
   @description - applies a MD5 hash to any string given.
                  This function will be used on any mac
                  address recorded by the application.
   @author - mah60
   @params - mac - char * - mac address to have the MD5 hash applied to it
   @params - output - char * - the char array that the hashed array will be assigned to.
   @return - MD5 Hash -  String - the mac address with a MD5 hash applied to it.
*/
void hashMacAddress(char * mac, char * output) {
  MD5Builder md5;
  md5.begin();
  md5.add(mac);
  md5.calculate();
  md5.getChars(output);
}

/**
   @summary - check if mac address is in the filter array.
   @description - Check if mac address is in the filter array.
                  returns true, if mac address is in the filter.
   @author - mah60
   @params - mac - char * - mac address wanting to be checked.
   @return - None
*/
bool filterCheck(char * mac) {
  // loop through filters
  for (int f = 0; f < filterCount; f++) {
    // get through filter mac addess
    char filter[20];
    getCharInRange(filteredMacAddress, commaLoc[f] + 1, commaLoc[f + 1], filter);
    if (!strcmp(filter, mac)) { // compare two char arrays
      return true;
    }
  }
  return false;
}

/**
   @summary - records variables for the database and stores it.
   @description - will hash the macaddress and store the wanted
                  variables to the txt file or database.
   @author - mah60
   @params - rssi - int32_t - rssi for the packets
   @params - userMac - char * - the mac address from the callback function of the package
   @return - None
*/
void recordData(int32_t rssi, char * userMac) {
  // filter the mac address, to remove unwanted ones
  if (filterCheck(userMac)) {
    // open text file - to upload data
    char * fileLoc = "recordings.txt";
    File fileName = SD.open(fileLoc, FILE_WRITE);
    if (fileName) { // connect to file
      // write data to txt file
      // apply one-way hash to mac addres to anonymise
      char hashedMac[50];
      hashMacAddress(userMac, hashedMac);
      fileName.print(hashedMac);
      fileName.print(",");
      fileName.print(trackerMacAddress);
      fileName.print(",");
      fileName.print(startDateTime);
      fileName.print(",");
      // get timestamp of amount of seconds since start up, millis resets every 49 days
      float runTime = getRunTime(); // divide millis by 1000 to get seconds
      fileName.print(runTime);
      fileName.print(",");
      fileName.print(rssi);
      fileName.print(",\n");
      fileName.close();
    } else {
      // if the file didn't open, print an error:
      Serial.println("error opening file----");
    }
  }
}

/**
   @summary - callback function when packets are found.
   @description - callback function will print out the packets details
             then forward the appropiate details to be stored onto the device.
   @author - mah60
   @params - buff - unit8_t - packet structure
   @params - len - unit16_t - the length of the packet
   @return - None
*/
void wifi_tracker_packet_handler(uint8_t *buff, uint16_t len) {
  /**
     https://blog.podkalicki.com/esp8266-wifi-sniffer/ - project site
     https://github.com/lpodkalicki/blog/blob/master/esp8266/016_wifi_sniffer/main.c - github code
     20/07/2019 ;
     This code was used to help develop this callback handler and the structs used to translate the package reading to
     string.
  */

  // First layer: convert type structure to generic SDK structure
  const wifi_promiscuous_pkt_t *ppkt = (wifi_promiscuous_pkt_t *)buff;
  // Second layer: create pointer to where the 802.1 packet is within the structure
  const wifi_ieee80211_packet_t *ipkt = (wifi_ieee80211_packet_t *)ppkt->payload;
  // Third layer : define pointers to 802.1 header and payload
  const wifi_ieee80211_mac_hdr_t *hdr = &ipkt->hdr;
  // create char array to store mac address
  char address[40]; // 0-17 -> Reciever address; 19-36 -> Sender address;
  for (int i = 0; i < 2; i++) { // get the reciever and sender mac address
    for (int x = 0; x < 6; x++) {  // loop through ints returned
      //char * macPart = decToChar();
      long num = 0;
      if (i == 0) { // if i is 0 get reciever address
        num = hdr->addr1[x];
      } else { // if 1 get sender address
        num = hdr->addr2[x];
      }
      // get hex values for mac address
      // store as char to record data
      char macPart[20];
      decToHex(num, macPart);
      // get char array position location
      int index = x * 3;
      if (i == 1) {
        index += 18;
      }
      // add mac part to char array
      address[index] = macPart[0];
      address[index + 1] = macPart[1];
      if (index == 15) {
        address[index + 2] = ','; //  add to end of mac address
      } else if ( index == 33) {
        address[index + 2] = '\0'; // end char array
      } else {
        address[index + 2] = ':'; // fill between mac parts
      }
    }
  }
  // get address values
  char add1[18], add2[18];
  getCharInRange(address, 0, 17, add1);
  getCharInRange(address, 18, 35, add2);
  // make sure mac address is not a null mac address
  char * nullMac = "FF:FF:FF:FF:FF:FF";
  char userMac[18];
  if (strcmp(add1, nullMac)) { // compare addresses
    strcpy(userMac, add1);
  } else  if (strcmp(add2, nullMac)) {
    strcpy(userMac, add2);
  } else {
    // record mac address
    recordData((int32_t)ppkt->rx_ctrl.rssi, add1);
    strcpy(userMac, add1);
  }
  // record mac address and rssi
  recordData((int32_t)ppkt->rx_ctrl.rssi, userMac);

}

/**
   @summary - turns on promiscous mode.
   @description - will turn on promiscuous mode and
                  disconnect the wifi to intercept
                  packages.
   @author - mah60
   @params - None
   @return - None
*/
void enablePromiscuousMode() {
  // disconnect from the internet to enter promicuous mode
  wifi_promiscuous_enable(0);
  WiFi.disconnect();

  // Set tracker callback and activate promiscous mode again
  wifi_set_promiscuous_rx_cb(wifi_tracker_packet_handler);
  wifi_promiscuous_enable(1);
}


#endif wifiAndPromiscuousMode.h
