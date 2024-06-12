import struct
import time

import serial


class Modbus485:
    def __init__(self, _rs485):
        self.rs485 = _rs485

    def modbus485_send(self, data):
        ser = self.rs485
        self.modbus485_clear_buffer()
        try:
            ser.write(serial.to_bytes(data))
        except Exception as e:
            print("Modbus485: Failed to write data:", e)
            return 0
        return

    def modbus485_read(self):
        ser = self.rs485
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            out = ser.read(bytesToRead)
            data_array = [b for b in out]
            print("Received Data:", data_array)
            return data_array
        return []

    def modbus485_clear_buffer(self):
        ser = self.rs485
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            out = ser.read(bytesToRead)
            print("Buffer:", out)

    def modbus485_read_adc(self):
        ser = self.rs485
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            out = ser.read(bytesToRead)
            data_array = [b for b in out]
            print(data_array)
            if len(data_array) > 7:
                array_size = len(data_array)
                value = data_array[array_size - 4] * 256 + data_array[array_size - 3]
                return value
        else:
            return 400
        return 404

    def modbus485_read_big_endian(self):
        ser = self.rs485
        bytesToRead = ser.inWaiting()
        return_array = [0, 0, 0, 0]
        if bytesToRead > 0:
            out = ser.read(bytesToRead)
            data_array = [b for b in out]
            print(data_array)

            if len(data_array) >= 7:
                return_array[0] = data_array[5]
                return_array[1] = data_array[6]
                return_array[2] = data_array[3]
                return_array[3] = data_array[4]
                print("Modbus485: Raw Data:", return_array)

                [value] = struct.unpack(">f", bytearray(return_array))
                return value
        else:
            return 400
        return 404


class SensorRelayController:
    relay_commands = {
        1: ([1, 6, 0, 0, 255, 201, 138], [1, 6, 0, 0, 0, 137, 202]),
        2: ([2, 6, 0, 0, 255, 201, 185], [2, 6, 0, 0, 0, 137, 249]),
        3: ([3, 6, 0, 0, 255, 200, 104], [3, 6, 0, 0, 0, 136, 40]),
        4: ([4, 6, 0, 0, 255, 201, 223], [4, 6, 0, 0, 0, 137, 159]),
        5: ([5, 6, 0, 0, 255, 200, 144], [5, 6, 0, 0, 0, 136, 78]),
        6: ([6, 6, 0, 0, 255, 200, 61], [6, 6, 0, 0, 0, 136, 127]),
        7: ([7, 6, 0, 0, 255, 201, 236], [7, 6, 0, 0, 0, 137, 172]),
        8: ([8, 6, 0, 0, 255, 201, 19], [8, 6, 0, 0, 0, 137, 83]),
    }

    soil_temperature_command = [10, 3, 0, 6, 0, 1, 101, 112]
    soil_moisture_command = [10, 3, 0, 7, 0, 1, 52, 176]

    def __init__(self, modbus):
        self.modbus = modbus

    def get_sensor_data(self):
        # Get soil temperature
        self.modbus.modbus485_send(self.soil_temperature_command)
        time.sleep(1)
        soil_temp = self.modbus.modbus485_read_big_endian()

        # Get soil moisture
        self.modbus.modbus485_send(self.soil_moisture_command)
        time.sleep(1)
        soil_moist = self.modbus.modbus485_read_big_endian()

        return soil_temp, soil_moist

    def control_relay(self, relay_num, state):
        if relay_num in self.relay_commands:
            command = (
                self.relay_commands[relay_num][0]
                if state
                else self.relay_commands[relay_num][1]
            )
            self.modbus.modbus485_send(command)
            time.sleep(1)
        else:
            print(f"Invalid relay number: {relay_num}")


if __name__ == "__main__":
    try:
        ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
    except Exception as e:
        print("Modbus485: Failed to open port:", e)

    m485 = Modbus485(ser)
    controller = SensorRelayController(m485)

    # # Test relay ON/OFF
    # for i in range(1, 9):
    #     controller.control_relay(i, True)
    # time.sleep(2)
    # for i in range(1, 9):
    #     controller.control_relay(i, False)

    # Test sensor data retrieval
    soil_temp, soil_moist = controller.get_sensor_data()
    print(f"Soil Temperature: {soil_temp}")
    print(f"Soil Moisture: {soil_moist}")
