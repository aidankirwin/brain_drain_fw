import threading
import time

class MotorControl(threading.Thread):
    def __init__(self, data_buffer, target_icp, is_draining):
        super().__init__(daemon=True)  # Daemon thread to run in background
        self.interval = 1  # 1 Hz update rate timer
        self.data_buffer = data_buffer
        self.running = True
        self.proportional_gain = 0.1  # Proportional gain for control response
        self.flow_to_step = 0.01  # Conversion factor from flow rate to step delay
        self.target_icp = target_icp  # Target ICP value for control logic
        self.is_draining = is_draining  # Initial drainage state is False (not draining)

    def run(self):
        while self.running:
            control_batch = self.data_buffer.fetch_buffer('icp', 'control')
            if control_batch is not None:
                self.delay_time = self.calculate_step_response(control_batch, self.is_draining)
            
            time.sleep(self.interval)
    
    def calculate_step_response(self, control_batch, is_draining):
        icp_difference = 0
        delay_time = None
        if len(control_batch) > 0:
            icp_difference = sum(control_batch) / len(control_batch) - self.target_icp
            delay_time = icp_difference * self.proportional_gain
        if icp_difference <= 0 or not is_draining:
            delay_time = None  # No drainage if ICP is below target or if drainage is turned off
        return delay_time
    
    def update_target_icp(self, new_target):
        self.target_icp = new_target
        print(f"Updated target ICP to: {self.target_icp}")

    def fetch_drainage_state(self, is_draining):
        self.is_draining = is_draining
        print(f"{'Draining' if self.is_draining else 'Not Draining WOOOOOOOO'}")
    
    def stop(self):
        self.running = False