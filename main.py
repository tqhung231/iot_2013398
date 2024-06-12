import json
import random
import time

from adafruit_mqtt import Adafruit_MQTT

# relay_mqtt = Adafruit_MQTT("relay.json")
# time.sleep(5)
sensor_mqtt = Adafruit_MQTT("config.json")
time.sleep(5)

while True:
    # feed = random.choice(relay_mqtt.feeds)
    # relay_mqtt.client.publish(feed, random.randint(0, 1))

    # feed = random.choice(sensor_mqtt.feeds)
    # sensor_mqtt.client.publish(feed, random.randint(0, 1))

    feed = "cmd"
    value = {
        "cmd": "relay",
        "relay": random.randint(1, 8),
        "state": random.randint(0, 1),
    }
    value = json.dumps(value)
    sensor_mqtt.client.publish(feed, value)

    time.sleep(5)
