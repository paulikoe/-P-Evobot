#include <SPI.h>
#include "SparkFunAutoDriver.h"
#include "util/delay.h" // Turns out, using the Arduino "delay" function
                        //  in a library constructor causes the program to
                        //  hang if the constructor is invoked outside of
                        //  setup() or hold() (i.e., the user attempts to
                        //  create a global of the class.

// Constructors
AutoDriver::AutoDriver(int CSPin, int resetPin, int busyPin)
{
  _CSPin = CSPin;
  _resetPin = resetPin;
  _busyPin = busyPin;
  
  SPIConfig();
}

AutoDriver::AutoDriver(int CSPin, int resetPin)
{
  _CSPin = CSPin;
  _resetPin = resetPin;
  _busyPin = -1;

  SPIConfig();
}

AutoDriver::AutoDriver()
{
	
}

void AutoDriver::attach(Adafruit_MCP23017 * mcp, int CSPin, int resetPin)
{
	_CSPin = CSPin;
	_resetPin = resetPin;
	_busyPin = -1;
	_mcp = mcp;

	SPIConfig();
}

void AutoDriver::SPIConfig()
{
  _mcp->pinMode(_CSPin, OUTPUT);//pinMode(_CSPin, OUTPUT);
  _mcp->digitalWrite(_CSPin, HIGH);//digitalWrite(_CSPin, HIGH);
  _mcp->pinMode(_resetPin, OUTPUT);//pinMode(_resetPin, OUTPUT);

  if (_busyPin != -1) pinMode(_busyPin, INPUT_PULLUP);
 
  SPI.begin();
 
  hardHiZ(); //put the bridges in Hi-Z state before the reset.
  _delay_ms(5);
  
  _mcp->digitalWrite(_resetPin, LOW);
  _delay_ms(5);
  _mcp->digitalWrite(_resetPin, HIGH);
  _delay_ms(5);
}

int AutoDriver::busyCheck(void)
{
  if (_busyPin == -1)
  {
    if (getParam(STATUS) & 0x0002) return 0;
    else                           return 1;
  }
  else 
  {
    if (digitalRead(_busyPin) == HIGH) return 0;
    else                               return 1;
  }
}
