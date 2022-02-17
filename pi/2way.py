import smbus2
import time
import json
import paho.mqtt.client as mqtt 


#global config
config = "th"

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe("IC.embedded/Erasmus/user")
#	print("data type: ", type(rc)) 
#	if str(rc) == 'th':
#		print("valid th")

def on_message(client, userdata, msg):
#might want to check more exact input eg 2 characters
	print(msg.topic+" "+str(msg.payload))
	msg.payload = msg.payload.decode("utf-8")	
	if msg.payload == "th" or msg.payload == "accel":
		global config
		config = msg.payload 
		print("valid: ",msg.payload)

bus = smbus2.SMBus(1)
#bus = smbus2.SMBus(2)

#20 is ctrl reg, 1Hz, xyz enabled
bus.write_byte_data(0x18, 0x20, 0x17)

time.sleep(0.5)

client = mqtt.Client()

client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
 
client.on_connect = on_connect
client.on_message = on_message


client.connect("test.mosquitto.org",port=8884)

client.loop_start()

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

	accel_data = {
		"x-axis" : x,
		"y-axis" : y,
		"z-axis" : z,
	#	"humidity" : humid,
	#	"temp" : temp,
	}

	th_data = {
		"humidity" : humid,
		"temp" : temp,
	}


	msg_accel = json.dumps(accel_data)
	msg_th = json.dumps(th_data)
#	print(msg_accel)
	print("THIS IS THE CONFIG!!!: ",config)
#	MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_accel)

	if(config == "accel"):
                MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_accel)
                print(msg_accel)

	if(config == "th"):
		MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_th)
		print(msg_th)


#	time.sleep(1)
	time.sleep(2)
