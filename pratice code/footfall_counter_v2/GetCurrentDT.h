#ifndef GetCurrentDT.h
#define GetCurrentDT.h

/**
   @summary - get timestamp from the internet if connected to wifi.
   @description - will get a data time time stamp from a website and
                  return a string of data that gives the exact time
                  of call if connected to wifi. The code was aquired
                  from; https://github.com/arduino-libraries/NTPClient/issues/36
                  -> code modified to handle char array instead
   @author - mah60
   @params - output - char * - the char array that the date time stamp will be assigned to.
   @return - None
*/
void getTimeStampString(char * output) {
  time_t rawtime = timeClient.getEpochTime();
  struct tm * ti;
  ti = localtime (&rawtime);

  int year = ti->tm_year + 1900;
  char yearStr[20];
  itoa(year, yearStr, 10);
  strcat(output, yearStr);

  strcat(output, "-");

  int month = ti->tm_mon + 1;
  char monthStr[20];
  itoa(month, monthStr, 10);
  strcat(output, monthStr);

  strcat(output, "-");

  int day = ti->tm_mday;
  char dayStr[20];
  itoa(day, dayStr, 10);
  strcat(output, dayStr);

  strcat(output, "-");

  int hours = ti->tm_hour;
  char hoursStr[20];
  itoa(hours, hoursStr, 10);
  strcat(output, hoursStr);

  strcat(output, "-");

  int minutes = ti->tm_min;
  char minutesStr[20];
  itoa(minutes, minutesStr, 10);
  strcat(output, minutesStr);

  strcat(output, "-");

  int seconds = ti->tm_sec;
  char secondsStr[20];
  itoa(seconds, secondsStr, 10);
  strcat(output, secondsStr);
}

#endif GetCurrentDT.h
