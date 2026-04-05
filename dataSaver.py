import pandas as pd
import time

SAVE_DATA = True
FILE_NAME = 'apr4_test2'

# global/singleton data saver
# saves data (either passed as a buffer of 25 values or a single value) to one of 2 lists (sensor or motor), updates csv files every 5 minutes or when the program is stopped
# the type of data being saved is also passed in (ICP, load1, load2, motor_target_flow, motor_step_delay) and saved as a column in the csv file
class DataSaver:
    def __init__(self, filename):
        self.filename = filename
        self.sensor_data = []
        self.motor_data = []

        self.start_time = time.time()
        self.last_updated = time.time()

    def add_entry(self, entry, type):
        entry_time = time.time() - self.start_time
        if type == 'sensor':
            # entry is a dictionary with keys 'icp', 'load1', 'load2' and values are the corresponding readings
            # also append time to the entry
            entry['time'] = entry_time
            self.sensor_data.append(entry)
        elif type == 'motor':
            # entry is a dictionary with keys 'motor_target_flow', 'motor_step_delay' and values are the corresponding values
            # entry is a single value, so just save the entry_time
            entry['time'] = entry_time
            self.motor_data.append(entry)

        if time.time() - self.last_updated > 10:  # Update every 10s
            self.update_csv()
            self.last_updated = time.time()

    def update_csv(self):
        # update the two csv files with new data without overwriting old data
        if self.sensor_data:
            sensor_df = pd.DataFrame(self.sensor_data)
            sensor_df.to_csv(f'{self.filename}_sensor.csv', mode='a', header=not pd.io.common.file_exists(f'{self.filename}_sensor.csv'), index=False)
            self.sensor_data = []  # Clear the buffer after saving
        if self.motor_data:
            # format the motor data into a dataframe with columns 'time', 'motor_target_flow', 'motor_step_delay'
            motor_df = pd.DataFrame(self.motor_data)
            motor_df.to_csv(f'{self.filename}_motor.csv', mode='a', header=not pd.io.common.file_exists(f'{self.filename}_motor.csv'), index=False)
            self.motor_data = []  # Clear the buffer after saving

data_saver = DataSaver(FILE_NAME)