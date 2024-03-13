#Pin Info

#Connection info.

#Series change info.


trigger_pin_1 = 24
echo_pin_1 = 25
trigger_pin_2 = 26
echo_pin_2 = 27
trigger_pin_3 = 28
echo_pin_3 = 29
trigger_pin_4 = 30
echo_pin_4 = 31


pump: (52)
	transistor:
	collector = GND pump
	emittor = GND power source, GND Arduino
	base: arduino's 52 with resistor

  enA = 49;
	in1 = 50;
	in2 = 51;



headlightPin {53};
laserPin {48};



dust:
	red 5V
	black A15
	yellow GND
	white 22
	green GND
	blue (5V--resistor--blue)
	capacitor (GND--white_leg--capacitor--long_leg--blue)

rain:
	VCC 5V
	GND GND
	A0 A14


flame:
	A8-A12 A1-A5

smoke:
	1 A6
	2 A7
	3 A13
