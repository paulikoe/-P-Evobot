// 
// 
// 


#include "Syringe.h"
#include "Marlin.h"
#include <Arduino.h>





Syringe::Syringe() : syringeVerticalPos(), syringePlunger()
	{
	 //config the CS pin and reset pin for the NEMA8 stepper motor driver 
		 //config the CS pin and reset pin for the 25NCLA stepper motor driver 
	

	
	

	
}

void Syringe::attach(Adafruit_MCP23017 * mcp, int resetPin, int CS_PlungerPin, int CS_SyringePin){
		_mcp = mcp;
		_resetPin = resetPin;
		_CS_PlungerPin = CS_PlungerPin;
		_CS_SyringePin = CS_SyringePin;
		_homed = false;
		_found = false;
		_syringe_driver_found = true;
		_plunger_driver_found = true;
				
		syringeVerticalPos.attach(mcp, CS_SyringePin, resetPin);
		syringePlunger.attach(mcp, CS_PlungerPin, resetPin);
	
		//check communications
		if(syringeVerticalPos.getParam(CONFIG)!=0x2E88){
			_syringe_driver_found = false;
			//SERIAL_PROTOCOLLN("ERROR: The NEMA8 stepper motor driver is not responding.");
		}
				
		if(syringePlunger.getParam(CONFIG)!=0x2E88){
			//SERIAL_PROTOCOLLN("ERROR: The 25NCLA stepper motor driver is not responding.");
			_plunger_driver_found = false;
		}
		
		if(_syringe_driver_found || _plunger_driver_found)
			_found = true;
			
		if(_syringe_driver_found && _plunger_driver_found)
			_isSyringe = true;
		if(_syringe_driver_found && !_plunger_driver_found)
			_isGripper = true;
		if(!_syringe_driver_found && _plunger_driver_found)
			_isScanner = true;
		
		if(_syringe_driver_found){
			
			//==========================================//
			// Config of the NEMA8 stepper motor driver //
			//==========================================//
			syringeVerticalPos.configSyncPin(BUSY_PIN, 0);// BUSY pin low during operations;
			//  second parameter ignored.
		

			//Max values tested: acc and decc = 1500, speed = 1500.
			//Recommended fast values: acc/decc = 1000, speed = 1000. 
			syringeVerticalPos.configStepMode(STEP_FS_16);// 128 microsteps per step
			syringeVerticalPos.setMaxSpeed(500);           // 500 steps/s max (2.5 turns per second)
			syringeVerticalPos.setMinSpeed(50);               // 50 steps/s max (0.25 turns per second)
			syringeVerticalPos.setFullSpeed(600);          // microstepping disabled if the speed is more than 3turns per second
			syringeVerticalPos.setAcc(300);                // accelerate at 200 steps/s/s
			syringeVerticalPos.setDec(300);
			syringeVerticalPos.setSlewRate(SR_530V_us);    // Upping the edge speed increases torque.
			syringeVerticalPos.setOCThreshold(OC_1875mA);   // OC threshold 1875mA
			syringeVerticalPos.setPWMFreq(PWM_DIV_1, PWM_MUL_2); // 31.25kHz PWM freq PWM_DIV_1, PWM_MUL_2
			syringeVerticalPos.setOCShutdown(OC_SD_ENABLE);// enable shutdown on OC
			syringeVerticalPos.setVoltageComp(VS_COMP_DISABLE); // don't compensate for motor V
			syringeVerticalPos.setSwitchMode(SW_HARD_STOP );     // Switch is hard stop
			syringeVerticalPos.setOscMode(INT_16MHZ);      // for syringePlunger, we want 16MHz
			syringeVerticalPos.setParam(INT_SPD, 0x3FFF);  //parameter optimized for the NEMA8  
			syringeVerticalPos.setParam(ST_SLP, 0x8);	   //parameter optimized for the NEMA8 
			syringeVerticalPos.setParam(FN_SLP_ACC, 0x30); //parameter optimized for the NEMA8 
			syringeVerticalPos.setParam(FN_SLP_DEC, 0x30); //parameter optimized for the NEMA8 
			syringeVerticalPos.setAccKVAL(155);  //Don not exceed 185 in NEMA8 motor (0.6A maximum).
			syringeVerticalPos.setDecKVAL(155);	 //Don not exceed 185 in NEMA8 motor (0.6A maximum).
			syringeVerticalPos.setRunKVAL(155);	 //Don not exceed 185 in NEMA8 motor (0.6A maximum).
			syringeVerticalPos.setHoldKVAL(105); //This controls the holding current; keep it low. Don not exceed 128 in NEMA8 motor (0.6A maximum).
		
			//syringePlunger.setLoSpdOpt(true);  //Low Speed Optimization disabled
		
			syringeVerticalPos.hardStop();

			//===========================================//
			// Config of the 25NCLA stepper motor driver //
			//===========================================//
			if (_isSyringe)
			{
				syringePlunger.configSyncPin(BUSY_PIN, 0);// BUSY pin low during operations;
				//  second parameter ignored.
				

				//Max values tested: acc and decc = 96, speed = 288.
				//Recommended fast values: acc/decc = 96, speed = 200.
				syringePlunger.configStepMode(STEP_FS_128);   // 128 microsteps per step
				syringePlunger.setMaxSpeed(144);               // 144 steps/s max (6 turns per second)
				syringePlunger.setMinSpeed(3);               // 12 steps/s max (0.5 turns per second)
				syringePlunger.setFullSpeed(144);             // microstepping disabled if speed is more tha 6 turns per second
				syringePlunger.setAcc(48);                    // accelerate at 48 steps/s/s
				syringePlunger.setDec(48);
				syringePlunger.setSlewRate(SR_530V_us);       // Upping the edge speed increases torque.
				syringePlunger.setOCThreshold(OC_375mA);      // OC threshold 375mA
				syringePlunger.setPWMFreq(PWM_DIV_2, PWM_MUL_2); // 31.25kHz PWM freq
				syringePlunger.setOCShutdown(OC_SD_ENABLE);   // enable shutdown on OC
				syringePlunger.setVoltageComp(VS_COMP_DISABLE); // don't compensate for motor V
				syringePlunger.setSwitchMode(SW_HARD_STOP);        // Switch is hard stop
				syringePlunger.setOscMode(INT_16MHZ);         // for syringePlunger, we want 16MHz
				//  internal osc, 16MHz out.
				syringePlunger.setParam(INT_SPD, 0x3FFF);  //parameter optimized for the 25NCLA
				syringePlunger.setParam(ST_SLP, 0x91);	   //parameter optimized for the 25NCLA
				syringePlunger.setParam(FN_SLP_ACC, 0xA4); //parameter optimized for the 25NCLA
				syringePlunger.setParam(FN_SLP_DEC, 0xA4); //parameter optimized for the 25NCLA
				syringePlunger.setAccKVAL(255);//255     // We'll tinker with these later, if needed.
				syringePlunger.setDecKVAL(255);//255
				syringePlunger.setRunKVAL(255);//255
				syringePlunger.setHoldKVAL(50);//200    // This controls the holding current; keep it low.
				
				//syringePlunger.setLoSpdOpt(true);	//Low Speed Optimization disabled
			}
		}
		
		//============================================================//
		// Config of the NEMA17 stepper motor driver (scanner module) //
		//============================================================//
		if(_isScanner){
			syringePlunger.configSyncPin(BUSY_PIN, 0);// BUSY pin low during operations;
			//  second parameter ignored.
							

			//Max values tested: acc and decc = 96, speed = 288.
			//Recommended fast values: acc/decc = 96, speed = 200.
			syringePlunger.configStepMode(STEP_FS_128);   // 128 microsteps per step
			syringePlunger.setMaxSpeed(400);               // 400 steps/s max (1 turns per second = 8mm/s)
			syringePlunger.setMinSpeed(50);               // 50 steps/s max (0.125 turns per second = 1mm/s)
			syringePlunger.setFullSpeed(800);             // microstepping disabled if speed is more than 2 turns per second
			syringePlunger.setAcc(200);                    // accelerate at 200 steps/s/s
			syringePlunger.setDec(200);
			syringePlunger.setSlewRate(SR_530V_us);       // Upping the edge speed increases torque.
			syringePlunger.setOCThreshold(OC_3000mA);      // OC threshold 1875mA
			syringePlunger.setPWMFreq(PWM_DIV_2, PWM_MUL_2); // 31.25kHz PWM freq
			syringePlunger.setOCShutdown(OC_SD_ENABLE);   // enable shutdown on OC
			syringePlunger.setVoltageComp(VS_COMP_DISABLE); // don't compensate for motor V
			syringePlunger.setSwitchMode(SW_USER);        // Switch is not hard stop
			syringePlunger.setOscMode(INT_16MHZ);         // for syringePlunger, we want 16MHz
			//  internal osc, 16MHz out.
			syringePlunger.setAccKVAL(75);//255     // We'll tinker with these later, if needed.
			syringePlunger.setDecKVAL(75);//255
			syringePlunger.setRunKVAL(75);//255
			syringePlunger.setHoldKVAL(45);//200    // This controls the holding current; keep it low.
							
			//syringePlunger.setLoSpdOpt(true);	//Low Speed Optimization disabled
		}
}

uint8_t Syringe::isBusy(){
	if (_syringe_driver_found && _plunger_driver_found)
	{
		if(syringeVerticalPos.busyCheck() || syringePlunger.busyCheck())
			return 1;
		else
			return 0;
	}
	
	if (_syringe_driver_found)
	{
		if(syringeVerticalPos.busyCheck())
			return 1;
		else
			return 0;
	}else{
		if( syringePlunger.busyCheck())
			return 1;
		else
			return 0;
	}
}

float Syringe::getSyringePos() {
  return( syringeVerticalPos.getPos()/float( STEPS_PER_MM_SYRINGE) );
}

float Syringe::getPlungerPos() {
	if(_isSyringe){
		return( syringePlunger.getPos()/float( STEPS_PER_MM_PLUNGER));
	}else{
		//If is not a syringe and a plunger position is requested, then it is a scanner
		return( syringePlunger.getPos()/float( STEPS_PER_MM_SCANNER));
	}
  
}

void Syringe::moveSyringe(float mm){
	while(syringeVerticalPos.busyCheck()){
		//Wait until the current command is finished
	}
	syringeVerticalPos.goTo( (long) (mm * STEPS_PER_MM_SYRINGE));
}

void Syringe::movePlunger(float mm){
	while(syringePlunger.busyCheck()){
		//Wait until the current command is finished
	}
	if(_syringe_driver_found)
		syringePlunger.goTo( (long) (mm * STEPS_PER_MM_PLUNGER));
	else{
		syringePlunger.goTo( (long) (mm * STEPS_PER_MM_SCANNER));
	}
}

//Set the speed
void Syringe::setSpeedPlunger(int stepsPerS){
	while(syringePlunger.busyCheck()){
			//Wait until the current command is finished
	}
	syringePlunger.setMaxSpeed(stepsPerS);
}

void Syringe::setSpeedSyringe(int stepsPerS){
	while(syringeVerticalPos.busyCheck()){
			//Wait until the current command is finished
	}
	syringeVerticalPos.setMaxSpeed(stepsPerS);
}

//Set the acceleration
void Syringe::setAccPlunger(int stepsPerS2){
	while(syringePlunger.busyCheck()){
			//Wait until the current command is finished
	}
	syringePlunger.setAcc(stepsPerS2);
	syringePlunger.setDec(stepsPerS2);
}

void Syringe::setAccSyringe(int stepsPerS2){
	while(syringeVerticalPos.busyCheck()){
		//Wait until the current command is finished
	}
	syringeVerticalPos.setAcc(stepsPerS2);
	syringeVerticalPos.setDec(stepsPerS2);
}

//Get the speed
float Syringe::getSpeedPlunger(){
	return syringePlunger.getMaxSpeed();
}

float Syringe::getSpeedSyringe(){
	return syringeVerticalPos.getMaxSpeed();
}

//Get the acceleration
float Syringe::getAccPlunger(){
	return syringePlunger.getAcc();
}
float Syringe::getDecPlunger(){
	return syringePlunger.getDec(); 
}

float Syringe::getAccSyringe(){
	return syringeVerticalPos.getAcc();
}

float Syringe::getDecSyringe(){
	return syringeVerticalPos.getDec();
}

void Syringe::home() {
  plungerHome();
  syringeHome();
}

void Syringe::plungerHome(){
	
	int status;
	bool alreadyPressed = false;
	
	
	//Debug
	SERIAL_ECHOLN("Plunger Home: Start");
	
	//check the status of the switch
	if(_plunger_driver_found){
		status = syringePlunger.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		SERIAL_ECHO("Plunger switch status: ");
		SERIAL_ECHOLN(status);
	}
	
	/**********      plunger home      **********/
	
	if (_plunger_driver_found)
	{
		//check the status of the switch
		status = syringePlunger.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		
		//SERIAL_ECHO("Status: ");
		//SERIAL_ECHOLN(status);
		unsigned long time = millis();
		 
		if (status == SW_NOT_PRESSED){
			if(_isSyringe)
				syringePlunger.goUntil(RESET_ABSPOS, REV, 96);
			if(_isScanner)
				syringePlunger.goUntil(RESET_ABSPOS, REV, 200);
			SERIAL_ECHOLN("Plunger switch is not pressed. Going towards the switch");
			
			alreadyPressed  = false;
			while(syringePlunger.busyCheck()){
				//wait until reach the syringe switch
				status = syringePlunger.getStatus();
				status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
				
				if(status == SW_PRESSED){
					SERIAL_ECHO("Plunger: Going towards the switch. Status: ");
					SERIAL_ECHOLN(status);
					if(alreadyPressed){
						//syringePlunger.hardStop();
					}
					alreadyPressed = true;
				}
				if ((millis() - time) >30000){
					syringePlunger.hardStop();
					SERIAL_ECHO("Plunger home: TIMEOUT");
					break;
				}
			}
		}
		
		status = syringePlunger.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		
		if(status == SW_PRESSED){
			//the switch is pressed
			SERIAL_ECHOLN("Plunger switch is pressed. Releasing the switch");
			syringePlunger.releaseSw(RESET_ABSPOS, FWD);
			while(syringePlunger.busyCheck()){
				//wait until release the switch
				status = syringePlunger.getStatus();
				status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
				if(status == SW_NOT_PRESSED){
					SERIAL_ECHO("Plunger: Releasing the switch. Status: ");
					SERIAL_ECHOLN(status);
				}
			
			}
		}
	}       
}

void Syringe::syringeHome(){
	
	int status;
	bool alreadyPressed = false;
	
	
	//Debug
	SERIAL_ECHOLN("Syringe Home: Start");
	
	//check the status of the switch
	if(_syringe_driver_found){
		status = syringeVerticalPos.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		SERIAL_ECHO("Syringe switch status: ");
		SERIAL_ECHOLN(status);
	}
	
	
	
	/**********      syringe home      **********/
	
	if(_syringe_driver_found){
		//check the status of the switch
		status = syringeVerticalPos.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		
		if (status == SW_NOT_PRESSED){
			syringeVerticalPos.goUntil(RESET_ABSPOS, FWD, 150);
			SERIAL_ECHOLN("Syringe switch is not pressed. Going towards the switch");
			
			while(syringeVerticalPos.busyCheck()){
				//wait until reach the syringe switch
				
				status = syringeVerticalPos.getStatus();
				status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
				
				if(status == SW_PRESSED){
					SERIAL_ECHO("Syringe Going towards the switch. Status: ");
					SERIAL_ECHOLN(status);
					if(alreadyPressed){
						//syringeVerticalPos.hardStop();
					}
					alreadyPressed = true;
				}
			}
		}
		//Check the status of the switch
		status = syringeVerticalPos.getStatus();
		status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
		
		if (status == SW_PRESSED){
			SERIAL_ECHOLN("Syringe switch is pressed. Releasing the switch");
			syringeVerticalPos.releaseSw(RESET_ABSPOS, REV);
			while(syringeVerticalPos.busyCheck()){
				//wait until release the syringe switch
			
				status = syringeVerticalPos.getStatus();
				status = (status&0b100)>>2; //Switch bit: 0 open, 1 switched
				if(status == SW_NOT_PRESSED){
					SERIAL_ECHO("Syringe: Releasing the switch. Status: ");
					SERIAL_ECHOLN(status);
				}
		}
	
		}
	
	}
	
	
	
	_homed = true;
}

long Syringe::syringeHomeTest(){
	syringeVerticalPos.setSwitchMode(SW_USER );     // Switch is not hard stop
	//syringe home test
	syringeVerticalPos.goUntil(COPY_ABSPOS, FWD, 150);
	while(syringeVerticalPos.busyCheck()){
		//wait until reach the syringe switch
	}
	
	syringeVerticalPos.releaseSw(COPY_ABSPOS, REV);
	while(syringeVerticalPos.busyCheck()){
		//wait until release the syringe switch
	}
	syringeVerticalPos.setSwitchMode(SW_HARD_STOP );     // Switch is  hard stop
	return syringeVerticalPos.getMark();
	
}

long Syringe::plungerHomeTest(){
		syringePlunger.setSwitchMode(SW_USER);        // Switch is not hard stop
	
		//plunger home test
		syringePlunger.goUntil(COPY_ABSPOS, REV, 48);
		while(syringePlunger.busyCheck()){
			//wait until reach the syringe switch
		}
		
		syringePlunger.releaseSw(COPY_ABSPOS, FWD);
		while(syringePlunger.busyCheck()){
			//wait until release the switch
		}
		syringePlunger.setSwitchMode(SW_HARD_STOP);        // Switch is hard stop
		return syringePlunger.getMark();
}

boolean Syringe::isHomed(){
	return _homed;
}

boolean Syringe::isFound(){
	return _found;
}

boolean Syringe::isSyringeDriverFound(){
	return _syringe_driver_found;
}

boolean Syringe::isPlungerDriverFound(){
	return _plunger_driver_found;
}

void Syringe::syringeHardStop(){
	syringeVerticalPos.hardStop();
}
void Syringe::plungerHardStop(){
	syringePlunger.hardStop();
}
void Syringe::syringeSoftStop(){
		syringeVerticalPos.softStop();
}
void Syringe::plungerSoftStop(){
	syringePlunger.softStop();
}

void Syringe::printDriverStatus(){
	int statusS, statusP;
	if (_syringe_driver_found)
	{
		statusS = syringeVerticalPos.getStatus();
		SERIAL_PROTOCOL(" S ");
		SERIAL_PROTOCOL(statusS);
		//SERIAL_ECHO("Syringe Driver: ");
		//printDriverInfo(statusS);
	}
	
	if (_plunger_driver_found)
	{
		statusP = syringePlunger.getStatus();
		SERIAL_PROTOCOL(" P ");
		SERIAL_PROTOCOL(statusP);
		//SERIAL_ECHO("Plunger Driver: ");
		//printDriverInfo(statusP);
	}
	
}

void Syringe::printDriverStatusVerbose(){
	int statusS, statusP;
	if (_syringe_driver_found)
	{
		statusS = syringeVerticalPos.getStatus();
		//SERIAL_PROTOCOL(" S ");
		//SERIAL_PROTOCOL(statusS);
		SERIAL_ECHO("Syringe Driver: ");
		printDriverInfo(statusS);
	}
	
	if (_plunger_driver_found)
	{
		statusP = syringePlunger.getStatus();
		//SERIAL_PROTOCOL(" P ");
		//SERIAL_PROTOCOL(statusP);
		SERIAL_ECHO("Plunger Driver: ");
		printDriverInfo(statusP);
	}
	
}
void Syringe::printDriverInfo(int status){
	
	int step_loss = (status>>13)&0b11; //bits 14 and 13
	int ocd = (status>>12)&0b1; //bit 12
	int th_sd = (status>>11)&0b1; //bit 11
	int th_wrn = (status>>10)&0b1; //bit 10
	int uvlo = (status>>9)&0b1; //bit 9
	int wrong_cmd = (status>>8)&0b1; //bit 8
	int not_perf_cmd = (status>>7)&0b1; //bit 7
	int mot_status = (status>>5)&0b11; //bits 6 and 5
	int sw_evn = (status>>3)&0b1; //bits 3 
	int sw_f = (status>>2)&0b1; //bits 2 
	int busy = (status>>1)&0b1; //bits 1 
	int hiz = (status)&0b1; //bits 0 
	
	if(step_loss !=3){
		SERIAL_ECHO("step_loss=");
		SERIAL_ECHO(step_loss);
	}	
	if(ocd == 0)
		SERIAL_ECHO(" OCD ");

	if(th_sd == 0)
		SERIAL_ECHO(" TH_SD ");
		
	if(th_wrn == 0)
		SERIAL_ECHO(" TH_WRN ");
		
	if (uvlo == 0)
		SERIAL_ECHO(" UVLO ");
	
	if(wrong_cmd == 1)
		SERIAL_ECHO(" WRONG_CMD ");
	
	if(not_perf_cmd == 1)
		SERIAL_ECHO(" NOT_PERF_CMD ");
	
	if(sw_evn == 1)
		SERIAL_ECHO(" SW_EVN ");
	
	if(sw_f == SW_PRESSED)
		SERIAL_ECHO(" SW_PRESSED ");
	
	SERIAL_ECHO(" MOT_STATUS=");
	if (mot_status == 0)
		SERIAL_ECHO("STOP");
	if (mot_status == 1)
		SERIAL_ECHO("ACC");
	if (mot_status == 2)
		SERIAL_ECHO("DEC");
	if (mot_status == 3)
		SERIAL_ECHO("C_SPEED");

	if(busy == 0)
		SERIAL_ECHO(" BUSY ");
	
	if(hiz == 1)
		SERIAL_ECHO(" HIZ ");
		
	
	
	SERIAL_ECHOLN("");
	
}







