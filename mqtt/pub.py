import sys,time,json

import paho.mqtt.client as paho

running = True

def on_publish(client, userdata, mid):
    global running
    print("Message published!")
    client.disconnect() 
    running = False

client = paho.Client()
client.on_publish = on_publish

if client.connect("127.0.0.1", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)
client.loop_start()
name = input("Name: ")
weight = input("Weight: ")
lightDistance = input("Light Distance: ")

soundDistance = input("Sound Distance: ")

out_obj = {"Light Distance":lightDistance, "Sound Distance": soundDistance,"Weight":weight,"Name":name}

out_str = json.dumps(out_obj)

client.publish("test_topic",out_str, 0)

while running:
    pass



