import smbus2
import time
import json
import paho.mqtt.client as mqtt 

bus = smbus2.SMBus(1)

#20 is ctrl reg, 1Hz, xyz enabled
bus.write_byte_data(0x18, 0x20, 0x17)

time.sleep(0.5)


while(1):
	x1 = bus.read_byte_data(0x18,0x28)
	x2 = bus.read_byte_data(0x18,0x29)

	y1 = bus.read_byte_data(0x18,0x2a)
	y2 = bus.read_byte_data(0x18,0x2b)

	z1 = bus.read_byte_data(0x18,0x2c)
	z2 = bus.read_byte_data(0x18,0x2d)

	x = x1+x2*256
	if x>32767:
		x-=65546

	y = y1+y2*256
	if y>32767:
		y-=65546

	z = z1+z2*256
	if z>32767:
		z-=65546

#	print("accel x-axis: %d " %x)
#	print("accel y-axis: %d " %y)
#	print("accel z-axis: %d " %z)

	accel = {
		"x-axis" : x,
		"y-axis" : y,
		"z-axis" : z,
	}


	msg = json.dumps(accel)
	print(msg)


	time.sleep(0.1)
