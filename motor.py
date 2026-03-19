import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice, AngularServo

import time
import threading
from dataCollect import DataBuffer

class Motor(threading.Thread):
    def __init__(self, motor_control):
        super().__init__(daemon=True)  # Daemon thread to run in background
        self.motor_control = motor_control  # Pass data buffer
        self.running = True
        self.interval = 0.001
        # self.STEP_PIN = 6

        # GPIO.setup(self.STEP_PIN, GPIO.OUT)

    def run(self):
        try:
            while self.running:
                if self.motor_control.delay_time is None:
                    time.sleep(self.interval)  # Default delay if no control signal
                else:
                    print('motor')
                    # time.sleep(self.interval)
                    # GPIO.output(self.STEP_PIN, GPIO.HIGH)
                    # time.sleep(0.005)
                    # GPIO.output(self.STEP_PIN, GPIO.LOW)
                    # time.sleep(self.motor_control.delay_time)

        except KeyboardInterrupt:
            print("Stopped")