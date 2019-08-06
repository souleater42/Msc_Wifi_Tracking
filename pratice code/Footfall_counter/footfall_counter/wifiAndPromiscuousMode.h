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
   @params - mac - String - mac address to have the MD5 hash applied to it
   @return - MD5 Hash -  String - the mac address with a MD5 hash applied to it.
*/
String hashMacAddress(String mac) {
  MD5Builder md5;
  md5.begin();
  md5.add(mac);
  md5.calculate();
  return md5.toString();
}

/**
   @summary - records variables for the database and stores it.
   @description - will hash the macaddress and store the wanted
                  variables to the txt file or database.
   @author - mah60
   @params - rssi - int32_t - rssi for the packets
   @params - macAddress2 - String - the mac address for the reciever of the package
   @return - None
*/
void recordData(int32_t rssi, String userMac) {
  // apply one-way hash to mac addres to anonymise
  String hashedMac = hashMacAddress(userMac);
  // get timestamp of amount of seconds since start up, millis resets every 49 days
  float timeStamp = getRunTime(); // divide millis by 1000 to get seconds
  // format data to be added to file/database
  String record = hashedMac + "," + trackerMacAddress + "," + startDateTime + "," +
                  (String)timeStamp + "," + (String)rssi + ";";
  Serial.println(record);
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

  /* ADDR1 - Reciever  address*/
  String macAddress1 = String(hdr->addr1[0], HEX) + ':' + String(hdr->addr1[1], HEX) + ':' + String(hdr->addr1[2], HEX)
                       + ':' + String(hdr->addr1[3], HEX) + ':' + String(hdr->addr1[4], HEX) + ':' + String(hdr->addr1[5], HEX);
  /* ADDR2 Sender address*/
  String macAddress2 = String(hdr->addr2[0], HEX) + ':' + String(hdr->addr2[1], HEX) + ':' + String(hdr->addr2[2], HEX)
                       + ':' + String(hdr->addr2[3], HEX) + ':' + String(hdr->addr2[4], HEX) + ':' + String(hdr->addr2[5], HEX);
  String nullMac = "ff:ff:ff:ff:ff:ff";
  String userMac;
  if (macAddress1.equals(nullMac)) {
    userMac = macAddress2;
  } else if (macAddress2.equals(nullMac)) {
    userMac = macAddress1;
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
