#ifndef SdCard.h
#define SdCard.h

#define PIN_NUM_CS D8

/**
   @summary - makes a connection to the SD card.
   @description - Connects to the SD card through the CS pin
                and allows for data to be read or written to
                the SD module.
   @author - mah60
   @params - None
   @return - None
*/
void setupSD() {

  Serial.print("Initializing SD card...");

  if (!SD.begin(PIN_NUM_CS)) {
    Serial.println("initialization failed!");
    delay(1);
  }
  Serial.println("initialization done.");

}

/**
   @summary - read filters from the given csv file.
   @description - read filters from the given csv file,
                 the code will also fill the fillteredMacAddress 
                 variable, numOfFilIndex and commaLoc.

                 The will have all the mac addresses that can be 
                 read by the device and will allow the code to 
                 remove unwanted mac addresses. This char array
                 will be split up using ',', which will be referenced
                 by commaLoc. numOfFilIndex, will keep record of how 
                 many filters there are in filteredMacAddress.
   @author - mah60
   @params - fileLoc - char * - the location of the csv file that is being read.
   @return - None
*/
void getFilters(char * fileLoc) {
  // open file
  File fileName = SD.open(fileLoc, FILE_READ);
  if (fileName) { // continue if connected
    // intialise varaibles for reading
    int index = 0;
    int numOfFilIndex = 0;
    filteredMacAddress[index] = ',';
    commaLoc[numOfFilIndex] = index;
    index++;
    numOfFilIndex++;
    // read the file until there are no char left
    while (fileName.available()) {
      // get next char to be read
      char c = (char)fileName.read();
      if ( c == '\n') { // replace newline char with ','
        filteredMacAddress[index] = ',';
        commaLoc[numOfFilIndex] = index;
        numOfFilIndex++;
        index++;
        filterCount++;
      } else if (c == '\r') {
        // for return leave blank
      } else { // place wanted char into filteredMacAddress
        filteredMacAddress[index] = c;
        index++;
      }
    }
    // add null pointer reference
    filteredMacAddress[index] = '\0';
    fileName.close(); // close file
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening file");
  }
}

#endif SdCard.h
