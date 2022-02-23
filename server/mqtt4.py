import paho.mqtt.client as mqtt
import json
import time
import sys

co2_inside = 1
co2_outside = 1

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #replace these with inside/outside
    client.subscribe("IC.embedded/Erasmus/test")
    client.subscribe("IC.embedded/Erasmus/test2")

def on_message(client, userdata, msg):
    #print(msg.topic+" "+str(msg.payload))
    #msg.topic = msg.topic.decode("utf-8")
    #print("1: ",msg.payload)
    #print("payload: ",msg.payload)
    #print("msg type: ",type(msg))
    #print("payload type: ",type(msg.payload))
    #print("payload: ",msg.payload.getInt("co2"))
    value = msg.payload.decode("utf-8")
    value = value[8:]
    value = value.replace("}","")
    #print("string: ",value)
    #print("decode type: ",type(msg.payload))
    #print("2: ",msg.payload)
    #print(msg.payload['co2'])
    print(msg.topic)
    if msg.topic == "IC.embedded/Erasmus/test":
        global co2_inside
        co2_inside = int(value)
        #print("co2_inside_received: ", co2_inside)
    if msg.topic == "IC.embedded/Erasmus/test2":
        global co2_outside
        co2_outside = int(value)
        #print("co2_outside_received: ",co2_outside)
    #product['price'] = float(product['price'])


client = mqtt.Client()

client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")

client.on_connect = on_connect
client.on_message = on_message


client.connect("test.mosquitto.org",port=8884)


client.loop_start()    #non blocking
#client.loop()         #call once?
#client.loop_forever()      #blocking

while(1):
    #line = sys.stdin.readline()
    #parts = line.split()
    #if len(parts) > 0:
    #    client.publish("IC.embedded/Erasmus/user",line)
    #value = input("choose th or co2: \n")
    #client.publish("IC.embedded/Erasmus/user",value)

    print("co2_inside: ",co2_inside)
    print("co2_outside: ",co2_outside)
    if(co2_inside>co2_outside):
        print("outside is better")
    else:
	print("inside is better")
    time.sleep(3)
    


