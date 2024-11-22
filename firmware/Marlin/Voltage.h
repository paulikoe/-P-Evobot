/*
 * Voltage.h
 *
 * Created: 27/01/2015 17:00:31
 *  Author: anfv
 */ 


#ifndef VOLTAGE_H_
#define VOLTAGE_H_

#include "Marlin.h"

#define MAX_ANALOG_INPUTS 7
#define VOLT_0_PIN 3
//#define VOLT_1_PIN 4
//#define VOLT_2_PIN 5
//#define VOLT_3_PIN 9
//#define VOLT_4_PIN 10
//#define VOLT_5_PIN 11
//#define VOLT_6_PIN 12


extern float current_volt_0;

// public functions
void manage_voltage_inputs(); //manage voltage is called periodically.

FORCE_INLINE float getCurrentVoltage0() {
	return current_volt_0;
};

#endif /* VOLTAGE_H_ */