#ifndef generalFun.h
#define generalFun.h


/**
   @summary - get the run time of the device.
   @description - will return the run time of the device in
                  seconds once the timestamp for startDateTime
                  is collected.
   @author - mah60
   @params - None
   @return - runTime - float -  the amount of time the device has
                been running in seconds.
*/
float getRunTime() {
  return ((float)millis() - startMillis) / 1000;
}

#endif generalFun.h
