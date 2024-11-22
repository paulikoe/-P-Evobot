/*
 * Voltage.cpp
 *
 * Created: 27/01/2015 16:59:42
 *  Author: anfv
 */ 

#include "Marlin.h"
#include "Voltage.h"
#include "temperature.h"


//not used, only for testing purposes
void manage_voltage_inputs(void){
	
	static unsigned long previous_time = millis();
	
	if ( (millis()-previous_time) > 1000){
		
		SERIAL_ECHO("Voltage 0:");
		SERIAL_ECHOLN(current_volt_0/8/1024*5);
		previous_time = millis();
	}
	
}