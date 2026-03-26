import threading
import time
import numpy as np
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice, AngularServo

class MotorControl(threading.Thread):
    def __init__(self, data_buffer, target_icp, is_draining):
        super().__init__(daemon=True)  # Daemon thread to run in background
        self.interval = 0.1  # 1 Hz update rate timer
        self.data_buffer = data_buffer
        self.running = True
        self.target_icp = target_icp  # Target ICP value for control logic
        self.is_draining = is_draining  # Initial drainage state is False (not draining)

        # Pin definitions
        self.motor_pin = 13
        self.servo_pin = 12

        self.servo = AngularServo(self.servo_pin, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
        time.sleep(0.5)
        self.servo.detach()

        self.motor = PWMOutputDevice(self.motor_pin)
        self.delay_time = None

        self.is_irrigating = False

        self.startup = True

    def run(self):
        while self.running:
            if self.startup:
                self.servo.angle = 0
                time.sleep(0.5)
                self.servo.detach()
                self.startup = False

            control_batch = self.data_buffer.fetch_buffer('icp', 'control')
            if control_batch is not None:
                self.delay_time = self.calculate_step_response(control_batch, self.is_draining)

            if self.is_irrigating is True:
                self.is_irrigating = False
                self.irrigate()
            
            time.sleep(self.interval)
    
    def calculate_step_response(self, control_batch, is_draining):
        icp_difference = 0
        delay_time = None
        if len(control_batch) > 0:
            icp_difference = sum(control_batch) / len(control_batch) - self.target_icp

            compliance = 3
            flow = compliance * icp_difference

            # change in flow = change in pressure * compliance
            # for now assume compliance = 3

            # relationship between flow rate and step response approximately y = 0.12e^-0.0303x
            # where x = flow rate in mL/hr, and y is step delay in seconds

            print(f'ICP Difference = {icp_difference}, draining at {flow} mL/hr')
            delay_time = 0.12 * np.e ** (-0.0303 * flow)
            # delay_time = 1
            # delay_time = None

        if icp_difference <= 0 or not is_draining:
            delay_time = None  # No drainage if ICP is below target or if drainage is turned off
        return delay_time
    
    def update_target_icp(self, new_target):
        self.target_icp = new_target
        print(f"Updated target ICP to: {self.target_icp}")

    def fetch_drainage_state(self, is_draining):
        self.is_draining = is_draining
        print(f"{'Draining' if self.is_draining else 'Not Draining WOOOOOOOO'}")

    def irrigate(self):
        print('irrigating')
        self.servo.angle = 90
        time.sleep(0.5)
        self.servo.detach()

        for i in range(8):
                print("motor go")
                self.motor.value = 200/255.0  # Convert Arduino PWM (0–255) to 0–1
                time.sleep(1)

        # --- Motor OFF loop ---
        for i in range(1):
            print("motor stop")
            self.motor.value = 0
            time.sleep(1)

        self.servo.angle = 0
        time.sleep(0.5)
        self.servo.detach()
    
    def stop(self):
        self.running = False