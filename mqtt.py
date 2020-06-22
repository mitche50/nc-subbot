# TODO: Subscribe to MQTT
# TODO: On message, update the role for the provided discord ID if it is in the server
import paho.mqtt.client as mqtt
from datetime import datetime
import requests
import json
import os

from dotenv import load_dotenv
load_dotenv()


c = mqtt.Client()



def on_connect(client, userdata, flags, rc):
    """
    On connection to the MQTT server, automatically subscribe to merchant_order_requests topic
    """
    print("{}: Connected to Nano Repeat servers with result code {}".format(datetime.now(), str(rc)))
    print(f"subscribing to topic: {os.getenv('MERCHANT_ID')}")
    client.subscribe(f"{os.getenv('MERCHANT_ID')}")


def on_message(client, userdata, msg):
    try:
        print(msg.payload)
        info = json.loads(msg.payload)
        print(info['subscriber_id'])
        # print('r = requests.put("https://discord.com/api/guilds/{guild.id}/members/{user.id}/roles/{role.id}"')
    except Exception as e:
        print(e)
    
    # print(msg)


c.on_connect = on_connect
c.on_message = on_message
c.username_pw_set(os.getenv('MQTT_LOGIN'), password=os.getenv('MQTT_PW'))
c.connect(os.getenv('MQTT_HOST'), int(os.getenv('MQTT_PORT')))

c.loop_forever()