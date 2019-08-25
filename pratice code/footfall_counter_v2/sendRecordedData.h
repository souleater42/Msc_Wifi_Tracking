#ifndef sendRecordedData.h
#define sendRecordedData.h

/**
   @summary - will send the data collected to x device over wifi.
   @description - will send the data collected to another device
                  over the wifi to be processed. This will only be
                  done if the device is connected to the wifi and
                  can make a secure connection.
   @author - mah60
   @params - None
   @return - None
*/
void sendRecords() {
  if (!WiFi.status()) { // check if device is connected to wifi
    connectToWifi();
  }
  if (isWifi) { // only send data if connected to wifi
    Serial.println(previousTransmissionMillis);
    Serial.println("sent data");
  }
  enablePromiscuousMode();
}

#endif sendRecordedData.h
