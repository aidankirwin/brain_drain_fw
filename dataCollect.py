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

class KalmanVolumeFlow:
    def __init__(self, dt, process_var_flow=0.01, meas_var=1.0):
        self.dt = dt

        # State: [volume, flow]
        self.x = np.zeros((2, 1))

        # Covariance
        self.P = np.eye(2)

        # Matrices
        self.F = np.array([[1, dt],
                           [0, 1]])

        self.H = np.array([[1, 0]])

        self.Q = np.array([[0, 0],
                           [0, process_var_flow]])

        self.R = np.array([[meas_var]])

        self.initialized = False

    def update(self, volume_meas):
        z = np.array([[volume_meas]])

        # Initialize on first measurement
        if not self.initialized:
            self.x = np.array([[volume_meas],
                               [0]])
            self.initialized = True
            return self.x.flatten()

        # Prediction
        x_pred = self.F @ self.x
        P_pred = self.F @ self.P @ self.F.T + self.Q

        # Update
        y = z - self.H @ x_pred
        S = self.H @ P_pred @ self.H.T + self.R
        K = P_pred @ self.H.T @ np.linalg.inv(S)

        self.x = x_pred + K @ y
        self.P = (np.eye(2) - K @ self.H) @ P_pred

        return self.x.flatten()

class DataBuffer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True

        # Control flags
        self.running = True

        # Timing
        self.period = 0.0033  # ~300 Hz total loop

        # calibration models
        with open('model.pkl', 'rb') as handle:
            self.loaded_model = pickle.load(handle)

        self.lc_scale = 0.32830703
        self.lc_offset = -1634.5324180655623

        # Buffers
        self.max_length = 100
        self.display_icp_buffer = []
        self.control_icp_buffer = []

        self.display_load1_buffer = []
        self.control_load1_buffer = []
        self.flow_load1_buffer = []

        self.display_load2_buffer = []
        self.control_load2_buffer = []
        self.flow_load2_buffer = []

        # FILTERS
        self.sos_pressure = signal.butter(4, 20, btype='low', output='sos', fs=100)
        self.sos_loadcell = signal.butter(4, 0.5, btype='low', output='sos', fs=100)
        # Kalman parameters
        process_var = 1e-6  # process variance
        meas_var = 38791215.89354596 # from test data

        self.z_pressure = None
        self.z_load1 = None
        self.z_load2 = None

        self.kf_1 = KalmanVolumeFlow(
            1/100,
            process_var_flow=process_var,
            meas_var=meas_var
        )

        self.kf_2 = KalmanVolumeFlow(
            1/100,
            process_var_flow=process_var,
            meas_var=meas_var
        )

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
                    self.add_data(self.control_load1_buffer, value[0])
                    self.add_data(self.flow_load1_buffer, value[1])

                elif ch == 3:
                    self.add_data(self.display_load2_buffer, value)
                    self.add_data(self.control_load2_buffer, value[0])
                    self.add_data(self.flow_load2_buffer, value[1])

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

        reading = self.ads.read(ch)

        # Calibration curves and filtering
        if ch == 0: # pressure
            reading = self.loaded_model['poly'].transform(
                pd.DataFrame(reading.reshape(-1, 1), columns=self.loaded_model['poly'].feature_names_in_)
            )
            reading = self.loaded_model['quad_model'].predict(reading)
            reading = [0]

            # filtering
            if self.z_pressure is None:
                self.z_pressure = signal.sosfilt_zi(self.sos_pressure) * reading
            reading, self.z_pressure = signal.sosfilt(self.sos_pressure, [reading], self.z_pressure)
            return reading[0]

        elif ch == 1:    # load cell 1
            # Calibration
            reading = reading * self.lc_scale + self.lc_offset

            # filtering
            if self.z_pressure is None:
                self.z_pressure = signal.sosfilt_zi(self.sos_loadcell) * reading
            reading, self.z_load1 = signal.sosfilt(self.sos_loadcell, [reading], self.z_load1)

            x = self.kf_1.update(reading)
            return x[0], x[1]   # return weight and flow estimates

        elif ch == 2:    # load cell 2
            # Calibration
            reading = reading * self.lc_scale + self.lc_offset

            # filtering
            if self.z_load2 is None:
                self.z_load2 = signal.sosfilt_zi(self.sos_loadcell) * reading
            reading, self.z_load2 = signal.sosfilt(self.sos_loadcell, [reading], self.z_load2)

            x = self.kf_1.update(reading)
            return x[0], x[1]   # return weight and flow estimates

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