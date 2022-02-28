import smbus2
import time
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("IC.embedded/Erasmus/user")
    client.subscribe("IC.embedded/Erasmus/ext_sensor")

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	msg.payload = msg.payload.decode("utf-8")	

	global desired_temp
	global min_humid
	global max_humid
	global mode
	global enable   #or on
	print("a msg received")
	if msg.topic == "IC.embedded/Erasmus/user":
		print("msg received from user")
		desired_temp, min_humid, max_humid, mode, enable = msg.payload.split(',')
		print("desired_temp")
		print("min_humid")
		print("max_humid")
		print("mode")
		print("off")

		print("received mode: ",mode)
		desired_temp = float(desired_temp)
		min_humid = float(min_humid)
		max_humid = float(max_humid)
		enable = int(enable)

		if(enable == 0):
			mode = 5

	global ext_temp
	global ext_humid
	global ext_tvoc

	if msg.topic == "IC.embedded/Erasmus/ext_sensor":
		print("msg received from ext sensor")
		ext_temp,ext_humid,ext_tvoc = msg.payload.split(",")


def setup_aq_sensors():
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

def read_humid():
    bus.i2c_rdwr(meas_humid)
    time.sleep(0.1)
    read_result = smbus2.i2c_msg.read(0x40,2)
    bus.i2c_rdwr(read_result)

    humid = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
    humid = (125*humid/65536)-6
    return humid

def read_temp():
    bus.i2c_rdwr(meas_temp)
    time.sleep(0.1)
    read_result = smbus2.i2c_msg.read(0x40,2)
    bus.i2c_rdwr(read_result)

    temp = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
    temp = (175.72*temp/65536)-46.85
    return temp

def read_tvoc():         #might want to remove c02, clean up this function
    meas_co2 = smbus2.i2c_msg.write(0x5A,[0x02])
    bus.i2c_rdwr(meas_co2)
    read_result  = smbus2.i2c_msg.read(0x5A, 8)
    bus.i2c_rdwr(read_result)
    co2_high = (int.from_bytes(read_result.buf[0],'big')&(0b01111111))*256
    co2_low = int.from_bytes(read_result.buf[1],'big')
    tvoc_high = (int.from_bytes(read_result.buf[2],'big')&(0b01111111))*256
    tvoc_low = int.from_bytes(read_result.buf[3],'big')
    co2 = co2_high + co2_low
    tvoc = tvoc_high + tvoc_low
    if co2>=400 and co2<=8192:
        print("air quality: ",co2)
    else:
        print("invalid co2")
    if tvoc>=0 and tvoc<=1187:
        print("tvoc: ", tvoc)
    else:
        print("invalid tvoc")
    return tvoc

def process_data(mode,desired_temp,min_humid,max_humid,int_temp,ext_temp,int_humid,ext_humid,int_tvoc,ext_tvoc,window_status,heater_status,ac_status):

    print("process mode: ",mode)
    print("process mode type: " ,type(mode))
    #default values
    w_t = 0.6
    w_h = 0.2
    w_a = 0.2
    temp_thresh = 5

    if mode == 0 :
        print("mode: default")
    elif mode == 1 :
        print("mode: energy save")
        temp_thresh = 9999         #infinite  
    elif mode == 2 :
        print("mode: temp priority")
        temp_thresh = 2
    elif mode == 3 :
        print("mode: air quality priority")
        w_t = 0.4
        w_h = 0.2
        w_a = 0.4
    if mode == 4 :
        print("mode: humidity priority")
        w_t = 0.4
        w_h = 0.4
        w_a = 0.2
    elif mode == 5 :
        print("mode: control system off") #or automation off
        w_t = 0
        w_h = 0
        w_a = 0
        temp_thresh = 9999            #infinite  

    print("w_h: ",w_h)
    temp_cont = abs(int_temp - desired_temp) - abs(ext_temp - desired_temp)
    temp_cont = (temp_cont*100)/95    #range is -10 to 85

    if(int_humid<min_humid):
        int_humid_cont = min_humid - int_humid
    elif(int_humid>max_humid):
        int_humid_cont = int_humid - max_humid
    else:
        int_humid_cont = 0

    if(ext_humid<min_humid):
        ext_humid_cont = min_humid - ext_humid
    elif(ext_humid>max_humid):
        ext_humid_cont = ext_humid - max_humid
    else:
        ext_humid_cont = 0

    humid_cont = int_humid_cont - ext_humid_cont
    humid_cont = (humid_cont*100)/80   #range is 0 to 80

    air_cont =  - int_tvoc - ext_tvoc
    air_cont = (air_cont*100)/1187    #range is 0 to 1187 

    temp_achievable = ((abs(int_temp - desired_temp))<temp_thresh) & ((abs(ext_temp - desired_temp))<temp_thresh)

    #negative value mean inside better, mean close window
    window = w_t * temp_cont + w_h * humid_cont + w_a * air_cont   

    if(temp_achievable):
        if(int_temp-desired_temp)<0:
            ac_status = "off"
            heater_status = "on"
        else:
            ac_status = "on"
            heater_status = "off"
        #heater_status = (int_temp - desired_temp) <0
        #ac_status = (int_temp - desired_temp) >0
        #what happens if inside colder but outside hotter but window open, do we just let it adjust over time?

#    print("pre-process window_status: ",window_status)
    if(window<-10):  #window open
        window_status = "open"
    elif(window>10):
        window_status = "closed"
#    print("returned window_status: ",window_status)
    return window_status, heater_status, ac_status

    #led(17) = window_status
    #led(18) = heat
    #led(19) = cool


bus = smbus2.SMBus(1)

#air quality
setup_aq_sensors()

time.sleep(0.5)


#setup mqtt
client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org",port=8884)
client.loop_start()

#humidity and temperature read
meas_humid = smbus2.i2c_msg.write(0x40,[0xe5])
meas_temp = smbus2.i2c_msg.write(0x40,[0xe0])

#initialise values
mode = 0
desired_temp = 24
min_humid = 30
max_humid = 50
ext_temp = 20
ext_humid = 40
ext_tvoc = 0
heater_status = "off"
ac_status = "off"
window_status = "open"  #0 is open

while(1):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    int_temp = read_temp()  #do we need sleeps?
    int_humid = read_humid()
    int_tvoc = read_tvoc()

    window_status, heater_status, ac_status = process_data(mode,desired_temp,min_humid,max_humid,int_temp,ext_temp,int_humid,ext_humid,int_tvoc,ext_tvoc,window_status,heater_status,ac_status)

#    status = {    #fix terminology?, change to strings?
#        "temp" : int_temp,
#        "humid" : int_humid,
#        "tvoc" : int_tvoc,
#        "window status" : window_status,
#        "heater_status" : heater_status,
#        "ac_status" : ac_status,
#    }

    temp = str(int_temp) + "," + str(int_humid) + "," + str(int_tvoc) + "," + window_status + "," +  ac_status + "," + heater_status 
    print("msg: ",temp)
#    print("type check: ",temp)
#    msg = json.dumps(status)
#    print(msg)

    MSG_INFO = client.publish("IC.embedded/Erasmus/int_sensor",temp)

    time.sleep(1)

