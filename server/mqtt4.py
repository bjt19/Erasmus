import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("IC.embedded/Erasmus/test")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client()

client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")

client.on_connect = on_connect
client.on_message = on_message


client.connect("test.mosquitto.org",port=8884)


client.loop_start()    #non blocking
#client.loop()         #call once?
#client.loop_forever()      #blocking

while(1):
    value = input("choose th or co2: \n")
    client.publish("IC.embedded/Erasmus/user",value)

    time.sleep(3)
    


