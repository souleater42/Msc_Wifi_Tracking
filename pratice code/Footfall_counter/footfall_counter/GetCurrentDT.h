#ifndef GetCurrentDT.h
#define GetCurrentDT.h

/**
   @summary - get timestamp from the internet if connected to wifi.
   @description - will get a data time time stamp from a website and 
                  return a string of data that gives the exact time
                  of call if connected to wifi. The code was aquired
                  from; https://github.com/arduino-libraries/NTPClient/issues/36
   @author - mah60
   @params - None
   @return - None
*/
String getTimeStampString() {
   time_t rawtime = timeClient.getEpochTime();
   struct tm * ti;
   ti = localtime (&rawtime);

   uint16_t year = ti->tm_year + 1900;
   String yearStr = String(year);

   uint8_t month = ti->tm_mon + 1;
   String monthStr = month < 10 ? "0" + String(month) : String(month);

   uint8_t day = ti->tm_mday;
   String dayStr = day < 10 ? "0" + String(day) : String(day);

   uint8_t hours = ti->tm_hour;
   String hoursStr = hours < 10 ? "0" + String(hours) : String(hours);

   uint8_t minutes = ti->tm_min;
   String minuteStr = minutes < 10 ? "0" + String(minutes) : String(minutes);

   uint8_t seconds = ti->tm_sec;
   String secondStr = seconds < 10 ? "0" + String(seconds) : String(seconds);

   return yearStr + "-" + monthStr + "-" + dayStr + "-" +
          hoursStr + "-" + minuteStr + "-" + secondStr;
}

#endif GetCurrentDT.h
