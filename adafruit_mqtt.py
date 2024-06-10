import json
import sys

from Adafruit_IO import MQTTClient


class Adafruit_MQTT:
    def __init__(self, config):
        try:
            with open(config, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print("Error:", e)

        self.feeds = data["feeds"]

        client = MQTTClient(data["username"], "".join(data["key"]))
        client.on_connect = self.connected
        client.on_disconnect = self.disconnected
        client.on_message = self.message
        client.on_subscribe = self.subscribe
        client.connect()
        client.loop_background()
        self.client = client

    def connected(self, client):
        print("Connected ...")
        for feed in self.feeds:
            client.subscribe(feed)

    def subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribeb...")

    def disconnected(self, client):
        print("Disconnected...")

    def message(self, client, feed_id, payload):
        print("Received: " + payload + " from " + feed_id)
        # if feed_id == "nutnhan1":
        #     if payload == "0":
        #         writeSerial("1")
        #     else:
        #         writeSerial("2")
        # elif feed_id == "nutnhan2":
        #     if payload == "0":
        #         writeSerial("3")
        #     else:
        #         writeSerial("4")


def publishRandomData(client):
    import random

    sensor_type = random.choice([0, 1, 2])
    print("Publishing random data...")
    if sensor_type == 0:
        print("Temperature...")
        temp = random.randint(15, 60)
        client.publish("cambien1", temp)
        sensor_type = 1
    elif sensor_type == 1:
        print("Light...")
        light = random.randint(0, 500)
        client.publish("cambien2", light)
        sensor_type = 2
    elif sensor_type == 2:
        print("Humidity...")
        humi = random.randint(0, 100)
        client.publish("cambien3", humi)
        sensor_type = 0
