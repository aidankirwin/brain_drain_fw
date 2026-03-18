from gpiozero import OutputDevice
import time
import threading
from dataCollect import DataBuffer

class Motor(threading.Thread):
    def __init__(self, motor_control):
        super().__init__(daemon=True)  # Daemon thread to run in background
        self.motor_control = motor_control  # Pass data buffer
        self.running = True
        self.interval = 0.001
        self.STEP_PIN = 3
        self.step = OutputDevice(self.STEP_PIN)

    def run(self):
        try:
            while self.running:
                if self.motor_control.delay_time is None:
                    time.sleep(self.interval)  # Default delay if no control signal
                else:
                    self.step.on()
                    time.sleep(0.005)   # HIGH pulse (0.5 ms)
                    self.step.off()
                    time.sleep(self.motor_control.delay_time)  # Delay based on motor control logic

        except KeyboardInterrupt:
            print("Stopped")