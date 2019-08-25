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

/**
   @summary - turns decimal values to hex in value
   @description -
   @author - mah60
   @params - dec - int - number wanting to be turned to char
   @params - output - char * - the char array that the hex string will be assigned to.
   @return - None
*/
void decToHex(int dec, char * output) {
  // intialise variables
  char hexValue[20];
  char * hex = "0123456789ABCDEF";
  // divide by 16
  int index = 0;
  if (dec > 16) {
    while ( dec > 16) {
      int remainder = (dec % 16);
      dec = dec / 16;
      hexValue[index] = hex[remainder];
      index++;
    }

    // once below 1, means final value for char array
    hexValue[index++] = hex[dec];
    hexValue[index++] = '\0';
  } else if ( dec == 16) { // if 16 defualt to '10'
    hexValue[0] = '0';
    hexValue[1] = '1';
    hexValue[2] = '\0';
  } else {
    // if below 16 defualt to '0x',
    //x being the hex value for the number
    hexValue[0] = hex[dec];
    hexValue[1] = '0';
    hexValue[2] = '\0';
  }
  // now flip array

  for ( int i = 0; i < strlen(hexValue); i++) {
    int reverseIndex = (strlen(hexValue) - i) - 1;
    output[i] = hexValue[reverseIndex];
  }
  output[strlen(hexValue)] = '\0';
}

/**
   @summary - gets substring of char array in given range.
   @description - gets substring of char array in given range. Must be inbetween
                  the 0 and the strlen() value for the char array.

                  Will retrieve characters between the min and max value.
   @author - mah60
   @params - str - char * - original str to be substringed
   @params - int - mimimum - min value for the range
   @params - int - maximum - max value for the range
   @params - output - char * - the char array that the char array will be assigned to.
   @return - None
*/
void getCharInRange(char * str, int minimum, int maximum, char * output) {
  for (int i = 0; i < (maximum - minimum); i++) {
    output[i] = str[minimum + i];
  }
  output[(maximum - minimum)] = '\0';
}



#endif generalFun.h
