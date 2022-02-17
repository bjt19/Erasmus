import paho.mqtt.client as mqtt
import time

client = mqtt.Client()

client.tls_set(ca_certs="mosquitto.org.crt", certfile="client.crt",keyfile="client.key")
if client.connect("test.mosquitto.org",port=8884)==0:
	print("connection success")

i=1

while(1):
	MSG_INFO = client.publish("IC.embedded/Erasmus/test",i)

	mqtt.error_string(MSG_INFO.rc)
	i=i+1
	time.sleep(5)
