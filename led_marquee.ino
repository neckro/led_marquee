/*
    Accepts 8-bit hex representing a marquee column through serial port,
    then scrolls it on LED.
*/
#include <LedControl.h>

/* data, clock, load, number of devices */
LedControl lc=LedControl(10, 11, 12, 1);
uint8_t buffer[8];
int8_t position = 0;
int8_t count = 0;
uint8_t value = 0;
int16_t in = 0;

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 15);
  Serial.begin(9600);
  // initialize buffer
  for (int8_t i = 0; i < 8; i++) {
    buffer[i] = 0;
  }
}

void loop() {
  while (in = Serial.read()) {
    int8_t mult = ((1 - count) * 4);
    if (in > 96 && in < 103) { // 'a' through 'f'
      value += (in - 87) << mult;
    } else if (in > 47 && in < 58) { // '0' through '9'
      value += (in - 48) << mult;
    } else {
      // reset and stop reading on non-hex character
      if (in != -1) {
        count = 0;
        value = 0;
      }
      break;
    }
    count++;
    if (count == 2) {
      // two values read, perform output
      buffer[position] = value;
      for (int8_t i = 0; i < 8; i++) {
        int8_t p = (position - i + 8) % 8;
        lc.setRow(0, i, buffer[p]);
      }
      position = ((position + 1) % 8);
      count = 0;
      value = 0;
      break;
    }
  }
}
