import json
import os
import queue
import random
import sys
import time

import numpy as np
import pygame
import serial
from Adafruit_IO import MQTTClient

from modbus import Modbus485, SensorRelayController


class SmartRecyclingBin:
    def __init__(self, controller):
        self.controller = controller

        self.init_pygame()
        self.load_assets()

        self.pumpin = False
        self.pumpout = False
        self.mixer1 = False
        self.mixer2 = False
        self.mixer3 = False
        self.area1 = False
        self.area2 = False
        self.area3 = False

        self.sensorData = {
            "area1": {
                "temperature": 0,
                "humidity": 0,
                "moisture": 0,
            },
            "area2": {
                "temperature": 0,
                "humidity": 0,
                "moisture": 0,
            },
            "area3": {
                "temperature": 0,
                "humidity": 0,
                "moisture": 0,
            },
        }

        # Inittialize relay and sensor data
        self.controller.control_relay(1, False)
        self.controller.control_relay(2, False)
        self.controller.control_relay(3, False)
        self.controller.control_relay(4, False)
        self.controller.control_relay(5, False)
        self.controller.control_relay(6, False)
        self.controller.control_relay(7, False)
        self.controller.control_relay(8, False)
        for area in self.sensorData:
            (
                self.sensorData[area]["temperature"],
                self.sensorData[area]["humidity"],
                self.sensorData[area]["moisture"],
            ) = self.controller.get_sensor_data()

        # Initialize Adafruit IO
        with open("config.json", "r") as f:
            config = json.load(f)

        self.feeds = config["feeds"]

        client = MQTTClient(config["username"], "".join(config["key"]))
        client.on_connect = self.connected
        client.on_disconnect = self.disconnected
        client.on_message = self.message
        client.on_subscribe = self.subscribe
        client.connect()
        client.loop_background()
        self.client = client

        self.emptying_queue = queue.Queue()

    def connected(self, client):
        print("Connected ...")
        for feed in self.feeds:
            client.subscribe(feed)

    def subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribeb...")

    def disconnected(self, client):
        print("Disconnected...")
        sys.exit(1)

    def message(self, client, feed_id, payload):
        print("Received: " + payload + " from " + feed_id)

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Smart Recycling Bin Monitor")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def load_assets(self):
        self.background_color = (0, 0, 0)

    def run_pygame_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pygame.display.flip()
            pygame.time.delay(100)

        pygame.quit()
        sys.exit()

    def start(self):
        self.run_pygame_loop()


if __name__ == "__main__":
    try:
        ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
    except Exception as e:
        print("Modbus485: Failed to open port:", e)

    m485 = Modbus485(ser)
    controller = SensorRelayController(m485)

    app = SmartRecyclingBin(controller)
    app.start()
