import os
import sys
import numpy as np
import pygame
import random
import time
from Adafruit_IO import MQTTClient
import queue
import json


class SmartRecyclingBin:
    def __init__(self):
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
        
        with open("relay.json", "r") as f:
            relayConfig = json.load(f)
        
        with open("config.json", "r") as f:
            sensorConfig = json.load(f)

        AIO_USERNAME = "tqhung231"
        # Check if key.txt exists
        try:
            with open("key.txt", "r") as f:
                AIO_KEY = f.read()
        except FileNotFoundError:
            # Dummy key
            AIO_KEY = "aio_"
        client = MQTTClient(AIO_USERNAME, AIO_KEY)
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
        for feed in self.AIO_FEED_IDs:
            client.subscribe(feed)

    def subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribeb...")

    def disconnected(self, client):
        print("Disconnected...")
        sys.exit(1)

    def message(self, client, feed_id, payload):
        print("Received: " + payload + " from " + feed_id)
        if feed_id == "cambien1":
            self.set_bins("Biological", self.bins["Biological"]["weight"], int(payload))
        elif feed_id == "cambien2":
            self.set_bins("Plastic", self.bins["Plastic"]["weight"], int(payload))
        elif feed_id == "cambien3":
            self.set_bins("Battery", self.bins["Battery"]["weight"], int(payload))
        elif feed_id == "cannang1":
            self.set_bins("Biological", int(payload), self.bins["Biological"]["level"])
        elif feed_id == "cannang2":
            self.set_bins("Plastic", int(payload), self.bins["Plastic"]["level"])
        elif feed_id == "cannang3":
            self.set_bins("Battery", int(payload), self.bins["Battery"]["level"])
        elif feed_id == "nutnhan1":
            if payload == "1":
                self.emptying_queue.put("Biological")
        elif feed_id == "nutnhan2":
            if payload == "1":
                self.emptying_queue.put("Plastic")
        elif feed_id == "nutnhan3":
            if payload == "1":
                self.emptying_queue.put("Battery")

    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Smart Recycling Bin Monitor")
        self.font = pygame.font.Font(None, 36)
        self.clock = pygame.time.Clock()

    def load_assets(self):
        self.background_color = (0, 0, 0)
        self.button_color = (200, 200, 200)
        self.button_text_color = (0, 0, 0)
        self.bin_colors = {True: (255, 0, 0), False: (0, 255, 0)}

    def run_pygame_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for bin_type, button in self.empty_buttons.items():
                        if button.collidepoint(event.pos):
                            self.start_emptying_process(bin_type)

            self.check_new_images()

            self.screen.fill(self.background_color)
            y = 20
            x_base = 20
            x_offset_weight = 200
            x_offset_level = 400
            x_offset_button = 600
            button_width = 90
            button_height = 30

            for bin_type, data in self.bins.items():
                if data["emptying"] and (time.time() - data["empty_time"] >= 5):
                    self.finish_emptying(bin_type)

                is_full = (
                    data["weight"] >= self.bin_capacity
                    or data["level"] >= 100
                    or data["emptying"]
                )
                color = self.bin_colors[is_full]

                # Draw bin type
                bin_label = self.font.render(bin_type, True, color)
                self.screen.blit(bin_label, (x_base, y))

                # Draw weight
                weight_label = self.font.render(
                    f"Weight - {data['weight']}kg", True, color
                )
                self.screen.blit(weight_label, (x_base + x_offset_weight, y))

                # Draw level
                level_label = self.font.render(f"Level - {data['level']}%", True, color)
                self.screen.blit(level_label, (x_base + x_offset_level, y))

                # Draw empty button
                self.empty_buttons[bin_type] = pygame.Rect(
                    x_base + x_offset_button, y, button_width, button_height
                )
                pygame.draw.rect(
                    self.screen, self.button_color, self.empty_buttons[bin_type]
                )
                empty_label = self.font.render("Empty", True, self.button_text_color)
                self.screen.blit(empty_label, (x_base + x_offset_button + 10, y + 5))

                y += 40

            pygame.display.flip()
            # self.clock.tick(1)
            pygame.time.delay(5000)

        pygame.quit()
        sys.exit()

    def update_bins(self, trash_type, weight, level):
        self.bins[trash_type]["weight"] += weight
        self.bins[trash_type]["level"] += level
        if self.bins[trash_type]["level"] >= 100:
            self.bins[trash_type]["level"] = 100
        if (
            self.bins[trash_type]["weight"] >= self.bin_capacity
            or self.bins[trash_type]["level"] >= 100
        ):
            self.start_emptying_process(trash_type)

    def set_bins(self, trash_type, weight, level):
        self.bins[trash_type]["weight"] = weight
        self.bins[trash_type]["level"] = level
        if self.bins[trash_type]["level"] >= 100:
            self.bins[trash_type]["level"] = 100
        if (
            self.bins[trash_type]["weight"] >= self.bin_capacity
            or self.bins[trash_type]["level"] >= 100
        ):
            self.start_emptying_process(trash_type)

    def update_bins_and_publish(self, trash_type, weight, level):
        self.bins[trash_type]["weight"] += weight
        self.bins[trash_type]["level"] += level
        if self.bins[trash_type]["level"] >= 100:
            self.bins[trash_type]["level"] = 100
        if trash_type == "Biological":
            self.client.publish("cambien1", self.bins["Biological"]["level"])
            self.client.publish("cannang1", self.bins["Biological"]["weight"])
        elif trash_type == "Plastic":
            self.client.publish("cambien2", self.bins["Plastic"]["level"])
            self.client.publish("cannang2", self.bins["Plastic"]["weight"])
        elif trash_type == "Battery":
            self.client.publish("cambien3", self.bins["Battery"]["level"])
            self.client.publish("cannang3", self.bins["Battery"]["weight"])
        if (
            self.bins[trash_type]["weight"] >= self.bin_capacity
            or self.bins[trash_type]["level"] >= 100
        ):
            self.start_emptying_process(trash_type)

    def start_emptying_process(self, trash_type):
        if not self.bins[trash_type]["emptying"]:
            self.bins[trash_type]["emptying"] = True
            self.bins[trash_type]["empty_time"] = time.time()

    def finish_emptying(self, trash_type):
        print(f"{trash_type} bin emptied.")
        self.bins[trash_type]["weight"] = 0
        self.bins[trash_type]["level"] = 0
        self.bins[trash_type]["emptying"] = False
        if trash_type == "Biological":
            self.client.publish("cambien1", self.bins["Biological"]["level"])
            self.client.publish("cannang1", self.bins["Biological"]["weight"])
            self.client.publish("nutnhan1", "0")
        elif trash_type == "Plastic":
            self.client.publish("cambien2", self.bins["Plastic"]["level"])
            self.client.publish("cannang2", self.bins["Plastic"]["weight"])
            self.client.publish("nutnhan2", "0")
        elif trash_type == "Battery":
            self.client.publish("cambien3", self.bins["Battery"]["level"])
            self.client.publish("cannang3", self.bins["Battery"]["weight"])
            self.client.publish("nutnhan3", "0")

    def start(self):
        self.run_pygame_loop()


if __name__ == "__main__":
    app = SmartRecyclingBin("trash")
    app.start()
