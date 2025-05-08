import sys,json,time,dotenv,os
from influxdb_client_3 import InfluxDBClient3, Point

import paho.mqtt.client as paho
import certifi

dotenv.load_dotenv()

token = os.getenv("TOKEN")

org = "Gruppe 251"
host = "https://eu-central-1-1.aws.cloud2.influxdata.com"

db_client = InfluxDBClient3(host=host, token=token, org=org,ssl_ca_cert=certifi.where())

database="super"

def message_handling(client, userdata, msg):
    global db_client, write,database
    if msg.topic=="get_data":
        input_str = msg.payload.decode()
        print(input_str)
        input_obj = json.loads(input_str)

        name = input_obj["Name"]
        
        query = f"SELECT * FROM \"trivia\" WHERE \"Name\"=\'{name}\'"
        print(query)
        #Execute the query
        table = db_client.query(query=query, database=database, language='sql')

        print("SUI")

        #Convert to dataframe
        df = table.to_pandas().sort_values(by="time")
        print(df)
        
        time.sleep(1)
    elif msg.topic=="test_topic":
        input_str = msg.payload.decode()
        print(input_str)
        input_obj = json.loads(input_str)

        print(input_obj["Name"])
        print(input_obj["Weight"])
        print(input_obj["Light Distance"])
        print(input_obj["Sound Distance"])

        point = (
                Point("trivia")
                .tag("Name",input_obj["Name"])
                .field("Weight",input_obj["Weight"])
                .field("Light Distance",input_obj["Light Distance"])
                .field("Sound Distance",input_obj["Sound Distance"])
                
        )
        db_client.write(database=database,record=point)
        time.sleep(1)
        print("Succesfully wrote to database")



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("test_topic",qos=0)
    client.subscribe("get_data",qos=0)

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
