import json
import os
import queue
import sys
import time
import warnings

import pygame
import serial
from Adafruit_IO import MQTTClient

from modbus import Modbus485, Modbus485_, SensorRelayController
from watering.test import WateringPredictionModel

warnings.filterwarnings("ignore")


class SmartRecyclingBin:
    def __init__(self, controller):
        # Save the current stdout
        self.original_stdout = sys.stdout
        # Redirect stdout to devnull
        sys.stdout = open(os.devnull, "w")

        # Watering model
        dir = "watering"
        model_path = os.path.join(dir, "watering_prediction_model.h5")
        scaler_path = os.path.join(dir, "scaler.pkl")
        self.wateringModel = WateringPredictionModel(model_path, scaler_path)

        self.controller = controller

        self.pumpin = False
        self.pumpout = False
        self.mixer1 = False
        self.mixer2 = False
        self.mixer3 = False
        self.area1 = False
        self.area2 = False
        self.area3 = False

        self.soilData = {
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

        self.levelData = {
            "water": 100,
            "mixer1": 0,
            "mixer2": 0,
            "mixer3": 0,
        }

        self.monitorData = {
            "watering": {
                "area1": False,
                "area2": False,
                "area3": False,
            },
            "mixer": {
                "mixer1": False,
                "mixer2": False,
                "mixer3": False,
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

        for area in self.soilData:
            (
                self.soilData[area]["temperature"],
                self.soilData[area]["humidity"],
                self.soilData[area]["moisture"],
            ) = self.controller.get_soil_data()

        for area in self.soilData:
            input_data = {
                "Soil Moisture": self.soilData[area]["moisture"],
                "Temperature": self.soilData[area]["temperature"],
                "Soil Humidity": self.soilData[area]["humidity"],
            }
            prediction = self.wateringModel.preprocess_and_predict(input_data)
            self.monitorData["watering"][area] = True if prediction == 1 else False

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
        time.sleep(5)

        # Publish relay and sensor data to Adafruit IO
        relayValue = {
            "pumpin": self.pumpin,
            "pumpout": self.pumpout,
            "mixer1": self.mixer1,
            "mixer2": self.mixer2,
            "mixer3": self.mixer3,
            "area1": self.area1,
            "area2": self.area2,
            "area3": self.area3,
        }
        self.client.publish("relay", json.dumps(relayValue))

        soilValue = {
            "area1": self.soilData["area1"],
            "area2": self.soilData["area2"],
            "area3": self.soilData["area3"],
        }
        self.client.publish("soil", json.dumps(soilValue))

        levelValue = {
            "water": self.levelData["water"],
            "mixer1": self.levelData["mixer1"],
            "mixer2": self.levelData["mixer2"],
            "mixer3": self.levelData["mixer3"],
        }
        self.client.publish("level", json.dumps(levelValue))

        monitorValue = {
            "watering": self.monitorData["watering"],
            "mixer": self.monitorData["mixer"],
        }
        self.client.publish("monitor", json.dumps(monitorValue))

        self.init_pygame()
        self.load_assets()

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
        # Restore the original stdout
        sys.stdout = self.original_stdout
        print("Received: " + payload + " from " + feed_id)
        # Redirect stdout to devnull
        sys.stdout = open(os.devnull, "w")

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Smart Farm Monitor")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def load_assets(self):
        self.background_color = (0, 0, 0)

    def update_data(self):
        for area in self.soilData:
            (
                self.soilData[area]["temperature"],
                self.soilData[area]["humidity"],
                self.soilData[area]["moisture"],
            ) = self.controller.get_soil_data()

        for area in self.soilData:
            input_data = {
                "Soil Moisture": self.soilData[area]["moisture"],
                "Temperature": self.soilData[area]["temperature"],
                "Soil Humidity": self.soilData[area]["humidity"],
            }
            prediction = self.wateringModel.preprocess_and_predict(input_data)
            self.monitorData["watering"][area] = True if prediction == 1 else False

        # (
        #     self.levelData["water"],
        #     self.levelData["mixer1"],
        #     self.levelData["mixer2"],
        #     self.levelData["mixer3"],
        # ) = self.controller.get_level_data()

        for area in self.monitorData["watering"]:
            if self.monitorData["watering"][area]:
                self.levelData["water"] -= 5
        if self.levelData["water"] <= 50:
            self.levelData["water"] = 100

        # relayValue = {
        #     "pumpin": self.pumpin,
        #     "pumpout": self.pumpout,
        #     "mixer1": self.mixer1,
        #     "mixer2": self.mixer2,
        #     "mixer3": self.mixer3,
        #     "area1": self.area1,
        #     "area2": self.area2,
        #     "area3": self.area3,
        # }
        # self.client.publish("relay", json.dumps(relayValue))

        soilValue = {
            "area1": self.soilData["area1"],
            "area2": self.soilData["area2"],
            "area3": self.soilData["area3"],
        }
        self.client.publish("soil", json.dumps(soilValue))

        levelValue = {
            "water": self.levelData["water"],
            "mixer1": self.levelData["mixer1"],
            "mixer2": self.levelData["mixer2"],
            "mixer3": self.levelData["mixer3"],
        }
        self.client.publish("level", json.dumps(levelValue))

        monitorValue = {
            "watering": self.monitorData["watering"],
            "mixer": self.monitorData["mixer"],
        }
        self.client.publish("monitor", json.dumps(monitorValue))

    def display_data(self):
        self.screen.fill(self.background_color)
        y_offset = 50
        for area, data in self.soilData.items():
            text = (
                f"{area.upper()}: Temp={data['temperature']}°C, Humidity={data['humidity']}%, "
                + f"Moisture={data['moisture']}%"
            )
            self.render_text(text, 20, y_offset)
            y_offset += 40

        for area, data in self.monitorData["watering"].items():
            text = f"{area.upper()} Watering: {data}"
            self.render_text(text, 20, y_offset)
            y_offset += 40

        level_status = [
            f"Water Level={self.levelData['water']}%",
            f"Mixer1 Level={self.levelData['mixer1']}%, Mixer2 Level={self.levelData['mixer2']}%, "
            + f"Mixer3 Level={self.levelData['mixer3']}%",
        ]
        for status in level_status:
            self.render_text(status, 20, y_offset)
            y_offset += 40

        relay_status = [
            f"Pumpin={self.pumpin}, Pumpout={self.pumpout}",
            f"Mixer1={self.mixer1}, Mixer1={self.mixer2}, Mixer1={self.mixer3}",
            f"Area1={self.area1}, Area2={self.area2}, Area3={self.area3}",
        ]
        for status in relay_status:
            self.render_text(status, 20, y_offset)
            y_offset += 40

    def render_text(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x, y))

    def run_pygame_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update_data()
            self.display_data()
            pygame.display.flip()
            # self.clock.tick(30)
            pygame.time.delay(10000)

        pygame.quit()
        sys.exit()

    def start(self):
        self.run_pygame_loop()


if __name__ == "__main__":
    try:
        ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
    except Exception as e:
        ser = None
        print("Modbus485: Failed to open port:", e)

    m485 = Modbus485_(ser)
    controller = SensorRelayController(m485)

    app = SmartRecyclingBin(controller)
    app.start()
