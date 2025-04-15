import sys,json,time,dotenv,os
from influxdb_client_3 import InfluxDBClient3, Point

import paho.mqtt.client as paho

dotenv.load_dotenv()

token = os.getenv("TOKEN")

org = "Gruppe 251"
host = "https://eu-central-1-1.aws.cloud2.influxdata.com/"

db_client = InfluxDBClient3(host=host, token=token, org=org)

database="trivia"

def message_handling(client, userdata, msg):
    global db_client, write,database
    input_str = msg.payload.decode()
    print(input_str)
    input_obj = json.loads(input_str)

    print(input_obj["topic"])
    print(input_obj["question"])
    print(input_obj["answer"])

    point = (
            Point("trivia")
            .tag("topic",input_obj["topic"])
            .field(input_obj["question"],input_obj["answer"])
    )
    db_client.write(database=database,record=point)
    time.sleep(1)
    print("Succesfully wrote to database")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test_topic",qos=0)

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic (QoS: {granted_qos})")

client = paho.Client(client_id="jhonny")
client.on_message = message_handling
client.on_connect = on_connect
client.on_subscribe = on_subscribe

if client.connect("127.0.0.1", 1883, 60) != 0:
    print("Couldn't connect to the mqtt broker")
    sys.exit(1)


try:
    print("Press CTRL+C to exit...")
    client.loop_forever()
except Exception:
    print("Caught an Exception, something went wrong...")
finally:
    print("Disconnecting from the MQTT broker")
    client.disconnect()
