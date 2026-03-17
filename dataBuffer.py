import threading
import time

class DataBuffer(threading.Timer):
    def __init__(self):
        super().__init__(daemon=True)
        
        # Start sampling/buffering data immediately upon initialization
        self.max_length = 400
        self.buffers = {'icp_disp': [], 'icp_ctrl': [], 
                        'dvolume_disp': [], 'dvolume_ctrl': [],
                        'fvolume_disp': [], 'fvolume_ctrl': []}
        
        self.lock = threading.Lock()

    def run(self):
        # get data
        value = 1
        self.add_data(value)
        time.sleep(self.interval)

    # Attach value from sensor read to the buffer
    def add_data(self, value):
        with self.lock:
            # Probably won't trigger often, but just in case
            if len(self.buffer) >= self.max_length:
                self.buffer.pop(0)  # remove oldest data point
            # Add new data point to the buffer
            self.buffer.append(value)

    # Return the current buffer contents
    def fetch_buffer(self, buffer_name : str) -> list:
        with self.lock:
            batch = self.buffer[buffer_name]
            del self.buffer[buffer_name]
            return list(batch)
