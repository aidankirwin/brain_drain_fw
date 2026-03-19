import threading
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import copy
import numpy as np
import pandas as pd
from scipy import signal
import pickle

class DataBuffer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

        # Control flags
        self.running = True

        # Timing
        self.period = 0.0033  # ~300 Hz total loop

        with open('model.pkl', 'rb') as handle:
            self.loaded_model = pickle.load(handle)

        # Buffers
        self.max_length = 100
        self.display_icp_buffer = []
        self.control_icp_buffer = []

        self.display_load1_buffer = []
        self.control_load1_buffer = []

        self.display_load2_buffer = []
        self.control_load2_buffer = []

        # FILTERS
        '''filters = coefficients, pass to filter
        function along with state, and current value.
        do that each time we get a new sample.'''

        # I2C + ADC setup
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)

        # Optional: increase data rate (important!)
        self.ads.data_rate = 860  # max speed

        self.voltage_to_icp_factor = 10

        # Thread safety
        self.lock = threading.Lock()

        # Channels to read
        self.channels = [0, 1, 3]

    def run(self):
        next_time = time.perf_counter()

        while self.running:
            loop_start = time.perf_counter()
            
            for ch in self.channels:
                value = self.read_channel(ch)

                if ch == 0:
                    self.add_data(self.display_icp_buffer, value)
                    self.add_data(self.control_icp_buffer, value)

                elif ch == 1:
                    self.add_data(self.display_load1_buffer, value)
                    self.add_data(self.control_load1_buffer, value)

                elif ch == 3:
                    self.add_data(self.display_load2_buffer, value)
                    self.add_data(self.control_load2_buffer, value)

            loop_end = time.perf_counter()

            # ---- measurements ----
            loop_period = loop_end - loop_start

            print(f"Loop period: {loop_period:.6f}s | ")

            # ---- timing control ----
            next_time += self.period
            sleep_time = next_time - time.perf_counter()

            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                # We're lagging → reset schedule
                next_time = time.perf_counter()

    def read_channel(self, ch):
        # Small delay to allow conversion to settle

        reading = np.array(self.ads.read(ch))

        # Calibration curves and filtering
        if ch == 0: # pressure
            reading = self.loaded_model['poly'].transform(
                pd.DataFrame(reading.reshape(-1, 1), columns=self.loaded_model['poly'].feature_names_in_)
            )
            reading = self.loaded_model['quad_model'].predict(reading)

        elif ch == 1 or ch == 3:    # load cell
            # Calibration
            scale = 0.32830703
            offset = -1634.5324180655623
            reading = reading * scale + offset

        
        # Convert
        return reading

    def add_data(self, buffer, value):
        with self.lock:
            buffer.append(value)
            if len(buffer) > self.max_length:
                buffer.pop(0)

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