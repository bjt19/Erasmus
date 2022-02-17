import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message) :
    print("Received message:{} on topic{}".format(message.payload, message.topic))


client = mqtt.Client()
if client.connect("test.mosquitto.org",port=8884)==0:
    print("connection success")

while(1):
    print("Waiting")
    client.on_message = on_message

    client.subscribe("IC.embedded/Erasmus/test")
    client.loop()

    time.sleep(1)
    print("done")
#Erasmus/test
#MSG_INFO = client.publish("IC.embedded/Erasmus/test","im desktop")
#mqtt.error_string(MSG_INFO.rc)


#https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#subscribe-unsubscribe  getting started(example of client)