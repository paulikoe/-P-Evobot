/*
 * SYRINGE.h defines all the parameters of one syringe.
 *
 * Created: 25/09/2014 15:45:08
 *  Author: anfv
 */ 


#ifndef SYRINGE_H_
#define SYRINGE_H_

#include <inttypes.h>
#include <SparkFunAutoDriver.h>
#include <Adafruit_MCP23017.h>


//#define CS_PLUNGER 40
//#define CS_SYRINGE 65 
//#define RESET_L6470 44

#define STEPS_PER_MM_SYRINGE 16*4.24426
#define STEPS_PER_MM_PLUNGER 128*24
#define STEPS_PER_MM_SCANNER 128*25

#define SW_PRESSED 1
#define SW_NOT_PRESSED 0


class Syringe
{
	public:
	Syringe();
	void attach(Adafruit_MCP23017*, int, int, int);
	uint8_t isBusy();           // attach the given pin to the next free channel, sets pinMode, returns channel number or 0 if failure
	void moveSyringe(float);
	void movePlunger(float);
	void home();
	void syringeHome();
	void plungerHome();
	float getSyringePos();
	float getPlungerPos();
	boolean isHomed();
	boolean isFound();
	boolean isSyringeDriverFound();
	boolean isPlungerDriverFound();
	void setSpeedPlunger(int);
	void setSpeedSyringe(int);
	void setAccPlunger(int);
	void setAccSyringe(int);
	float getSpeedPlunger();
	float getSpeedSyringe();
	float getAccPlunger();
	float getAccSyringe();
	float getDecPlunger();
	float getDecSyringe();
	
	long syringeHomeTest();
	long plungerHomeTest();
	void syringeHardStop();
	void plungerHardStop();
	void syringeSoftStop();
	void plungerSoftStop();
	void printDriverStatus();
	void printDriverStatusVerbose();
	void printDriverInfo(int);

	private:
	uint8_t syringeIndex;               // index into the channel data for this syringe
	AutoDriver syringeVerticalPos;//Nema8
	AutoDriver syringePlunger;//25NCLA
	Adafruit_MCP23017 * _mcp;
	int _resetPin;
	int _CS_PlungerPin;
	int _CS_SyringePin;
	boolean _homed;
	boolean _found;
	boolean _syringe_driver_found;
	boolean _plunger_driver_found;
	boolean _isSyringe;
	boolean _isGripper;
	boolean _isScanner;
	
};

#endif /* SYRINGE_H_ */
