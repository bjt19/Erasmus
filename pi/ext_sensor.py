import smbus2
import time
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

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

def read_humid(curr_humid):
    bus.i2c_rdwr(meas_humid)
    time.sleep(0.1)
    read_result = smbus2.i2c_msg.read(0x40,2)
    bus.i2c_rdwr(read_result)

    humid = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
    new_humid = (125*humid/65536)-6
    if new_humid>=0 and new_humid <=80:
        return new_humid
    else:
        print("invalid humidity")
        return curr_humid

def read_temp(curr_temp):
    bus.i2c_rdwr(meas_temp)
    time.sleep(0.1)
    read_result = smbus2.i2c_msg.read(0x40,2)
    bus.i2c_rdwr(read_result)

    temp = int.from_bytes(read_result.buf[0]+read_result.buf[1],'big')
    new_temp = (175.72*temp/65536)-46.85
    if new_temp>=-10 and new_temp <=85:
        return new_temp
    else:
        print("invalid temp")
        return curr_temp

def read_tvoc(curr_tvoc):
    meas_co2 = smbus2.i2c_msg.write(0x5A,[0x02])
    bus.i2c_rdwr(meas_co2)
    read_result  = smbus2.i2c_msg.read(0x5A, 8)
    bus.i2c_rdwr(read_result)
    tvoc_high = (int.from_bytes(read_result.buf[2],'big')&(0b01111111))*256
    tvoc_low = int.from_bytes(read_result.buf[3],'big')
    new_tvoc = tvoc_high + tvoc_low
    if new_tvoc>=0 and new_tvoc<=1187:
        return new_tvoc
    else:
        print("invalid tvoc")
        return curr_tvoc

bus = smbus2.SMBus(1)

#air quality
setup_aq_sensors()

time.sleep(0.5)


#setup mqtt
client = mqtt.Client()
client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
client.on_connect = on_connect
client.connect("test.mosquitto.org",port=8884)
client.loop_start()

#humidity and temperature reads
meas_humid = smbus2.i2c_msg.write(0x40,[0xe5])
meas_temp = smbus2.i2c_msg.write(0x40,[0xe0])

#initialise values
temp_data = 22
humid_data = 40
tvoc_data = 0

while(1):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    temp_data = read_temp(temp_data)  #do we need sleeps?
    humid_data = read_humid(humid_data)
    tvoc_data = read_tvoc(tvoc_data)

    print("temp, humidity, tvoc")
    msg = str(temp_data) + "," + str(humid_data) + "," + str(tvoc_data)
    print(msg)

    MSG_INFO = client.publish("IC.embedded/Erasmus/ext_sensor",msg)

    time.sleep(1)

