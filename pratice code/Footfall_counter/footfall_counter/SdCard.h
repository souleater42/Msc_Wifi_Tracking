#ifndef SdCard.h
#define SdCard.h

#define PIN_NUM_CS D8

void setupSD() {

  Serial.print("Initializing SD card...");

  if (!SD.begin(PIN_NUM_CS)) {
    Serial.println("initialization failed!");
    delay(1);
  }
  Serial.println("initialization done.");

}

void writeSD(String fileLoc, String output) {
  File fileName = SD.open(fileLoc, FILE_WRITE);

  // if can connect to file, write to it
  if (fileName) {
    fileName.println(output);
    // close the file
    fileName.close();
  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening file");
  }
}

void getFilters(String fileLoc) {
  File fileName = SD.open(fileLoc, FILE_READ);
  if (fileName) {
    int countFilters = 0;
    String macAddressFilter = "";
    while (fileName.available()) {
      char c = (char)fileName.read();
      if (c != '\n') {
        macAddressFilter.concat((String)c);
      } else {
        macAddressFilter.concat(";");
        countFilters++;
        //Serial.println(macAddressFilter);
      }
    }
    String fillMacAddress[countFilters];
    String newMacAddress = "";
    int filterCount = 0;
    for (int i = 0; i < macAddressFilter.length(); i++) {
      if (macAddressFilter.charAt(i) != ';' && macAddressFilter.charAt(i) != '\r') {
        newMacAddress.concat(macAddressFilter.charAt(i));
      } else if (macAddressFilter.charAt(i) == ';') {
        fillMacAddress[filterCount] = newMacAddress;
        newMacAddress = "";
        filterCount++;
      }
    }
//    filteredMacAddress = (String)malloc(sizeof(String)*countFilters);
//    filteredMacAddress = fillMacAddress;

  } else {
    // if the file didn't open, print an error:
    Serial.println("error opening file");
  }
}

#endif SdCard.h
