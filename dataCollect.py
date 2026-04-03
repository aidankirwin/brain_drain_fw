import threading
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15 import AnalogIn, ads1x15
import numpy as np
import pandas as pd
from scipy import signal
import pickle
import copy
import random

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
        self.period = 0.0033  # ~300 Hz

        # Load calibration model
        with open('model.pkl', 'rb') as handle:
            self.loaded_model = pickle.load(handle)

        self.lc_scale = 0.32830703
        self.lc_offset = -1634.5324180655623
        self.load1_tare = None
        self.load2_tare = None

        # Buffer config
        self.max_length = 25

        self.buffers = {
            "icp": {
                "display": [],
                "control": []
            },
            "load1": {
                "display": [],
                "control": [],
                "flow": []
            },
            "load2": {
                "display": [],
                "control": [],
                "flow": []
            }
        }

        # Filters
        self.fs = 50
        self.sos_pressure = signal.butter(4, 3, btype='low', output='sos', fs=self.fs)
        self.sos_loadcell = signal.butter(4, 0.5, btype='low', output='sos', fs=self.fs)

        self.z_pressure = None
        self.z_load1 = None
        self.z_load2 = None

        # Kalman filters
        process_var = 1e-5
        meas_var = 38791215.89354596

        self.kf_1 = KalmanVolumeFlow(1/self.fs, process_var, meas_var)
        self.kf_2 = KalmanVolumeFlow(1/self.fs, process_var, meas_var)

        # I2C + ADC
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.mode = ads1x15.Mode.SINGLE
        self.ads.data_rate = 250

        # Thread safety
        self.lock = threading.Lock()

        # Channels
        self.channels = [0, 1, 2]
        # self.channels = [0]

        self.start_time = time.time()

    def run(self):
        next_time = time.perf_counter()

        while self.running:
            loop_start = time.perf_counter()

            for ch in self.channels:
                value = self.read_channel(ch)

                if ch == 0:
                    self.add_data("icp", "display", value)
                    self.add_data("icp", "control", value)

                elif ch == 1:
                    # drainage load cell
                    self.add_data("load1", "display", value[0])  # weight
                    self.add_data("load1", "control", value[0])
                    self.add_data("load1", "flow", value[1])

                elif ch == 2:
                    # flushing load cell
                    self.add_data("load2", "display", value[0])
                    self.add_data("load2", "control", value[0])
                    self.add_data("load2", "flow", value[1])

            loop_end = time.perf_counter()
            # print(f"Loop period: {loop_end - loop_start:.6f}s")

            # Timing control
            next_time += self.period
            sleep_time = next_time - time.perf_counter()

            if sleep_time > 0:
                # print(f'sleep for {sleep_time}')
                time.sleep(sleep_time)
            else:
                next_time = time.perf_counter()

    def read_channel(self, ch):

        if ch == 0:  # pressure
            reading = float(AnalogIn(self.ads, ads1x15.Pin.A0).value)
            reading_arr = np.atleast_1d(reading)
            reading_df = pd.DataFrame(
                reading_arr.reshape(-1, 1),
                columns=self.loaded_model['poly'].feature_names_in_
            )
            # reading_arr = self.loaded_model['poly'].transform(reading_df)
            # reading_arr = self.loaded_model['quad_model'].predict(reading_arr)
            # reading_arr = reading_arr + 1.6

            if self.z_pressure is None:
                self.z_pressure = signal.sosfilt_zi(self.sos_pressure) * reading_arr

            reading_arr, self.z_pressure = signal.sosfilt(
                self.sos_pressure, reading_arr, zi=self.z_pressure
            )
            return reading_arr[0]

        elif ch == 1:  # load cell 1
            reading = float(AnalogIn(self.ads, ads1x15.Pin.A1).value)
            reading_arr = np.atleast_1d(reading)
            reading_arr = reading_arr * self.lc_scale + self.lc_offset

            # if self.load1_tare is not None:
            #     reading_arr = reading_arr - self.load1_tare
            #     reading_arr = np.atleast_1d(np.max([0.0, reading_arr[0]]))

            # if self.z_load1 is None:
            #     self.z_load1 = signal.sosfilt_zi(self.sos_loadcell) * reading_arr

            # reading_arr, self.z_load1 = signal.sosfilt(
            #     self.sos_loadcell, reading_arr, zi=self.z_load1
            # )

            # if time.time() - self.start_time > 5:
            #     x = self.kf_1.update(reading_arr[0])
            # else:
            #     x = [0,0]
            #     x[0] = reading_arr[0]
            #     print(x[0])
            #     x[1] = 1
            # return x[0], x[1]
            return reading_arr[0], 1

        elif ch == 2:  # load cell 2
            reading = float(AnalogIn(self.ads, ads1x15.Pin.A2).value)
            reading_arr = np.atleast_1d(reading)
            reading_arr = reading_arr * self.lc_scale + self.lc_offset

            # if self.load2_tare is not None:
            #     reading_arr = reading_arr - self.load2_tare
            #     reading_arr = np.atleast_1d(np.max([0.0, reading_arr[0]]))

            # if self.z_load2 is None:
            #     self.z_load2 = signal.sosfilt_zi(self.sos_loadcell) * reading_arr

            # reading_arr, self.z_load2 = signal.sosfilt(
            #     self.sos_loadcell, reading_arr, zi=self.z_load2
            # )

            # if time.time() - self.start_time > 5:
            #     x = self.kf_2.update(reading_arr[0])
            # else:
            #     x = [0,0]
            #     x[0] = reading_arr[0]
            #     print(x[0])
            #     x[1] = 1
            # return x[0], x[1]

            return reading_arr[0], 1

    def add_data(self, sensor, stream, value):
        with self.lock:
            buf = self.buffers[sensor][stream]
            buf.append(value)
            if len(buf) > self.max_length:
                buf.pop(0)

    def fetch_buffer(self, sensor, stream):
        with self.lock:
            buf = self.buffers[sensor][stream]

            if len(buf) >= self.max_length:
                batch = copy.copy(buf)
                buf.clear()

                if sensor == 'icp' and time.time() - self.start_time < 4:
                    return None

                if sensor == 'load1':
                    if self.load1_tare is None:
                        print('Tared load cell 1')
                        self.load1_tare = np.mean(batch)
                        return None
                
                    if time.time() - self.start_time < 5:
                        return None
                
                if sensor == 'load2':
                    if self.load2_tare is None:
                        print('Tared load cell 2')
                        self.load2_tare = np.mean(batch)
                        return None
                
                    if time.time() - self.start_time < 4:
                        return None

                return batch

            return None

    def stop(self):
        self.running = False