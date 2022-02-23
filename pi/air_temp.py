import smbus2
import time
import json
import paho.mqtt.client as mqtt 


#global config
config = "co2"

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
	if msg.payload == "th" or msg.payload == "co2":
		global config
		config = msg.payload 
		print("valid: ",msg.payload)

bus = smbus2.SMBus(1)
#bus = smbus2.SMBus(2)

#accel, 20 is ctrl reg, 1Hz, xyz enabled
#bus.write_byte_data(0x18, 0x20, 0x17)

#air quality
meas_co2 = smbus2.i2c_msg.write(0x5A,[0x00])
bus.i2c_rdwr(meas_co2)
read_result  = smbus2.i2c_msg.read(0x5A, 1)
bus.i2c_rdwr(read_result)
meas_co2 = smbus2.i2c_msg.write(0x5A, [0xF4])
bus.i2c_rdwr(meas_co2)

meas_co2 = smbus2.i2c_msg.write(0x5A,[0x00])
bus.i2c_rdwr(meas_co2)
read_result  = smbus2.i2c_msg.read(0x5A, 1)
bus.i2c_rdwr(read_result)
print("air quality: Entering application mode") 
meas_co2 = smbus2.i2c_msg.write(0x5A, [0x01,0b00011000 ])
bus.i2c_rdwr(meas_co2)

meas_co2 = smbus2.i2c_msg.write(0x5A,[0x00])
bus.i2c_rdwr(meas_co2)
read_result  = smbus2.i2c_msg.read(0x5A, 1)
bus.i2c_rdwr(read_result)
print("Entering measuring mode")

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
	print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

	#humid
	bus.i2c_rdwr(meas_humid)
	time.sleep(0.1)
	read_result = smbus2.i2c_msg.read(0x40,2)
	bus.i2c_rdwr(read_result)

	humid = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
	humid = (125*humid/65536)-6
	#print("humid: ",humid)

	#temp
	bus.i2c_rdwr(meas_temp)
	time.sleep(0.1)
	read_result = smbus2.i2c_msg.read(0x40,2)
	bus.i2c_rdwr(read_result)

	temp = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
	temp = (175.72*temp/65536)-46.85
	#print("temp: ",temp)
	#temp
	#bus.write_byte_data(0x40,0,0xe3)
	#temp = bus.read_byte_data(0x40,0)	
	#print(humid)
	#print(temp)


	#data ready?
#	meas_co2 = smbus2.i2c_msg.write(0x5A,[0x00])
#	bus.i2c_rdwr(meas_co2)
#	read_result = smbus2.i2c_msg.read(0x5A,1)
#	bus.i2c_rdwr(read_result)
#	status = int.from_bytes(read_result.buf[0],'big')
#	print("status : ", bin(status))

	#raw data
#	meas_co2 = smbus2.i2c_msg.write(0x5A,[0x02])
#	bus.i2c_rdwr(meas_co2)
#	read_result = smbus2.i2c_msg.read(0x5A,2)
#	bus.i2c_rdwr(read_result)
#	raw = int.from_bytes(read_result.buf[0],'big')*256 + int.from_bytes(read_result.buf[1],'big')

    	#co2
	meas_co2 = smbus2.i2c_msg.write(0x5A,[0x02])
	bus.i2c_rdwr(meas_co2)
#	time.sleep(0.5)
	read_result  = smbus2.i2c_msg.read(0x5A, 8)
	bus.i2c_rdwr(read_result)
	#print("Getting results")
#	co2 = int.from_bytes(read_result.buf[0],'big')*256 + int.from_bytes(read_result.buf[1],'big')
	co2_high = (int.from_bytes(read_result.buf[0],'big')&(0b01111111))*256
	co2_low = int.from_bytes(read_result.buf[1],'big')
	co2 = co2_high + co2_low
	#co2 = int.from_bytes(read_result.buf[0],'big')
#	tvoc = int.from_bytes(read_result.buf[2],'big')*256 + int.from_bytes(read_result.buf[3],'big')
#	alg_status = int.from_bytes(read_result.buf[5],'big')
#	error_id = int.from_bytes(read_result.buf[6],'big')
	if co2>=400 and co2<=8192:
		print("air quality: ",co2)
	else:
		print("invalid co2")
#	print("binary air quality: ",bin(co2))
#	print("tvoc: ",tvoc)
#	print("alg_status: ",alg_status)
#	print("error_id: ", error_id)
#	print("raw data: ",raw)

#	print("accel x-axis: %d " %x)
#	print("accel y-axis: %d " %y)
#	print("accel z-axis: %d " %z)

	#accel_data = {
	#	"x-axis" : x,
	#	"y-axis" : y,
	#	"z-axis" : z,
	#	"humidity" : humid,
	#	"temp" : temp,
	#}

	th_data = {
		"humidity" : humid,
		"temp" : temp,
	}

	air_data = {
        	"co2" : co2,
    	}

	#msg_accel = json.dumps(accel_data)
	msg_th = json.dumps(th_data)
	msg_co2 = json.dumps(air_data)
#	print(msg_accel)
	print("config: ",config)
#	MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_accel)

	if(config == "co2"):
       		MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_co2)
        	print(msg_co2)

	if(config == "th"):
		MSG_INFO = client.publish("IC.embedded/Erasmus/test",msg_th)
		print(msg_th)

	#MSG_INFO = client.publish("IC.embedded/Erasmus/test2","hello")
	time.sleep(1)
#	time.sleep(2)
