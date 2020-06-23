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
        if info['status'] == 'active':
            r = requests.put(
                f"https://discord.com/api/guilds/{os.getenv('GUILD_ID')}/members/{info['subscriber_id']}/roles/{os.getenv('ROLE_ID')}", 
                headers={'Authorization': f'Bot {os.getenv("TOKEN")}'}
            )
            message_content = {'content': 'Your role has been added successfully!  Thank you for your donation.'}
            m = requests.post(
                f"https://discord.com/api/users/@me/channels",
                headers={'Authorization': f'Bot {os.getenv("TOKEN")}'},
                json={'recipient_id': f'{info["subscriber_id"]}'}
            )
            channel_response = json.loads(m.text)
            m = requests.post (
                f"https://discord.com/api/channels/{channel_response['id']}/messages",
                headers={'Authorization': f'Bot {os.getenv("TOKEN")}'},
                json=message_content
            )
                
    except Exception as e:
        print(e)
    
    # print(msg)


c.on_connect = on_connect
c.on_message = on_message
c.username_pw_set(os.getenv('MQTT_LOGIN'), password=os.getenv('MQTT_PW'))
c.connect(os.getenv('MQTT_HOST'), int(os.getenv('MQTT_PORT')))

c.loop_forever()