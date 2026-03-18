import threading
import time
import copy
import random

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class DataBuffer(threading.Timer):
    def __init__(self):
        super().__init__(function=self.run, interval=0.001)   # daemon=True for simulation
        self.daemon = True

        # Start sampling/buffering data immediately upon initialization
        self.running = True
        self.max_length = 20
        self.display_icp_buffer = []
        self.control_icp_buffer = []
        self.display_load1_buffer = []
        self.control_load1_buffer = []
        self.display_load2_buffer = []
        self.control_load2_buffer = []

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.voltage_to_icp_factor = 10

        self.lock = threading.Lock()

    # Sample at 10 Hz
    def run(self):
        # read from ads1115
        voltage = self.ads.read(0)
        value = voltage * self.voltage_to_icp_factor

        self.add_data_display(value)
        self.add_data_control(value)

    # Attach value from sensor read to the buffer
    def add_data_display(self, value):
        with self.lock:
            # Probably won't trigger often, but just in case
            if len(self.display_icp_buffer) >= self.max_length:
                self.display_icp_buffer.pop(0)  # remove oldest data point
            # Add new data point to the buffer
            self.display_icp_buffer.append(value)

    # Attach value from sensor read to the buffer
    def add_data_control(self, value):
        with self.lock:
            # Probably won't trigger often, but just in case
            if len(self.control_icp_buffer) >= self.max_length:
                self.control_icp_buffer.pop(0)  # remove oldest data point
            # Add new data point to the buffer
            self.control_icp_buffer.append(value)

    # Return the current buffer contents (for plotting)
    def fetch_display_buffer(self):
        with self.lock:
            if len(self.display_icp_buffer) >= self.max_length:
                batch = copy.copy(self.display_icp_buffer)
                self.display_icp_buffer.clear()
                return list(batch)  # return a copy of the batch for plotting
            return None  # Not enough data to release yet
        
    def fetch_control_buffer(self):
        with self.lock:
            if len(self.control_icp_buffer) >= self.max_length:
                batch = copy.copy(self.control_icp_buffer)
                self.control_icp_buffer.clear()
                return list(batch)  # return a copy of the batch for control logic
            return None  # Not enough data to release yet
    
    def stop(self):
        self.running = False