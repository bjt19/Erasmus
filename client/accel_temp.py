import smbus2
import time
import json
import paho.mqtt.client as mqtt 

bus = smbus2.SMBus(1)
#bus = smbus2.SMBus(2)

#20 is ctrl reg, 1Hz, xyz enabled
bus.write_byte_data(0x18, 0x20, 0x17)

time.sleep(0.5)

client = mqtt.Client()

client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
if client.connect("test.mosquitto.org",port=8884)==0:
	print("connection success")

#start humidity read, temp is read as byproduct
meas_humid = smbus2.i2c_msg.write(0x40,[0xe5])
meas_temp = smbus2.i2c_msg.write(0x40,[0xe0])

while(1):
	x1 = bus.read_byte_data(0x18,0x28)
	x2 = bus.read_byte_data(0x18,0x29)

	y1 = bus.read_byte_data(0x18,0x2a)
	y2 = bus.read_byte_data(0x18,0x2b)

	z1 = bus.read_byte_data(0x18,0x2c)
	z2 = bus.read_byte_data(0x18,0x2d)

	#humid
	bus.i2c_rdwr(meas_humid)
	time.sleep(0.1)
	read_result = smbus2.i2c_msg.read(0x40,2)
	bus.i2c_rdwr(read_result)

	humid = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
	humid = (125*humid/65536)-6
	print("humid: ",humid)

	#temp
	bus.i2c_rdwr(meas_temp)
	time.sleep(0.1)
	read_result = smbus2.i2c_msg.read(0x40,2)
	bus.i2c_rdwr(read_result)

	temp = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
	temp = (175.72*temp/65536)-46.85
	print("temp: ",temp)
	#temp
	#bus.write_byte_data(0x40,0,0xe3)
	#temp = bus.read_byte_data(0x40,0)	
	#print(humid)
	#print(temp)


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

	sensor_data = {
		"x-axis" : x,
		"y-axis" : y,
		"z-axis" : z,
		"humidity" : humid,
		"temp" : temp,
	}


	msg = json.dumps(sensor_data)
	print(msg)
	MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg)

#	time.sleep(1)
	time.sleep(2)
