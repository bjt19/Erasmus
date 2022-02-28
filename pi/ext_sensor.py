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

#humidity and temperature read
meas_humid = smbus2.i2c_msg.write(0x40,[0xe5])
meas_temp = smbus2.i2c_msg.write(0x40,[0xe0])

while(1):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    temp_data = read_temp()  #do we need sleeps?
    humid_data = read_humid()
    tvoc_data = read_tvoc()


    status = {    #fix terminology?, change to strings?
        "temp" : temp_data,
        "humid" : humid_data,
        "tvoc" : tvoc_data,
    }

    msg = json.dumps(status)
    print(msg)

    MSG_INFO = client.publish("IC.embedded/Erasmus/ext_sensor",msg)

    time.sleep(1)

