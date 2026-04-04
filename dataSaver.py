import pandas as pd
import time

SAVE_DATA = True
FILE_NAME = 'brain_drain_data'

# global/singleton data saver
# saves data (either passed as a buffer of 25 values or a single value) to one of 2 lists (sensor or motor), updates csv files every 5 minutes or when the program is stopped
# the type of data being saved is also passed in (ICP, load1, load2, motor_target_flow, motor_step_delay) and saved as a column in the csv file
class DataSaver:
    def __init__(self, filename):
        self.filename = filename
        self.sensor_data = []
        self.motor_data = []
        
        # also save time stamps of new entries
        self.sensor_times = []
        self.motor_times = []

        self.start_time = time.time()
        self.last_updated = time.time()

    def add_entry(self, entry, type):
        entry_time = time.time()
        if type == 'sensor':
            # entry is a dictionary with keys 'icp', 'load1', 'load2' and values are the corresponding readings
            # entry is 25 values sampled at 50Hz, so it represents 0.5 seconds of data
            # generate a time array for the 25 values starting from entry_time and going back in time with a step of 0.02 seconds
            time_array = [entry_time - i*0.02 for i in range(len(entry))]
            self.sensor_data.append(entry)
            self.sensor_times.append(time_array)
        elif type == 'motor':
            # entry is a dictionary with keys 'motor_target_flow', 'motor_step_delay' and values are the corresponding values
            # entry is a single value, so just save the entry_time
            self.motor_data.append(entry)
            self.motor_times.append(entry_time)

        if time.time() - self.last_updated > 30:  # Update every 30s
            self.update_csv()
            self.last_updated = time.time()

    def update_csv(self):
        # update the two csv files with new data without overwriting old data
        if self.sensor_data:
            # format the sensor data into a dataframe with columns 'time', 'icp', 'load1', 'load2'
            sensor_df = pd.DataFrame(self.sensor_data, columns=['icp', 'load1', 'load2'])
            sensor_df['time'] = self.sensor_times
            sensor_df.to_csv(f'{self.filename}_sensor.csv', mode='a', header=not pd.io.common.file_exists(f'{self.filename}_sensor.csv'), index=False)
            self.sensor_data = []  # Clear the buffer after saving
        if self.motor_data:
            # format the motor data into a dataframe with columns 'time', 'motor_target_flow', 'motor_step_delay'
            motor_df = pd.DataFrame(self.motor_data, columns=['motor_target_flow', 'motor_step_delay'])
            motor_df['time'] = self.motor_times
            motor_df.to_csv(f'{self.filename}_motor.csv', mode='a', header=not pd.io.common.file_exists(f'{self.filename}_motor.csv'), index=False)
            self.motor_data = []  # Clear the buffer after saving

data_saver = DataSaver(FILE_NAME)