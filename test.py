import sys
import time
import signal
import threading
import tkinter as tk

from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory

from gpiozero import OutputDevice
from time import sleep

import time
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice, AngularServo


def gpio_test_loop():

    # Use BCM pin numbering
    GPIO.setmode(GPIO.BCM)

    # Pin definitions
    step_pin = 6
    motor_pin = 13
    servo_pin = 12

    # Setup pins
    GPIO.setup(step_pin, GPIO.OUT)

    # PWM motor (equivalent to analogWrite)
    motor = PWMOutputDevice(motor_pin)

    # Servo setup
    servo = AngularServo(servo_pin, min_angle=0, max_angle=180)

    # Delay settings
    delay_time = 0.01  # 10 ms

    try:
        while True:

            # --- Motor ON loop ---
            for i in range(50):
                print("motor go go go")
                motor.value = 200/255.0  # Convert Arduino PWM (0–255) to 0–1
                time.sleep(1)

            # --- Motor OFF loop ---
            for i in range(50):
                print("motor stoooooop")
                motor.value = 0

            # --- Stepper pulse loop ---
            for i in range(50):
                print("motor go go go")
                GPIO.output(step_pin, GPIO.HIGH)
                time.sleep(0.005)
                GPIO.output(step_pin, GPIO.LOW)
                time.sleep(delay_time)

            # --- Servo movement ---
            for i in range(1):
                servo.angle = 180
                time.sleep(1)
                servo.angle = 0
                time.sleep(1)

            # Optional: "detach" equivalent (stop sending signal)
            servo.detach()

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        GPIO.cleanup()

# TKINTER UI

class App:
    def __init__(self, root):
        self.root = root
        self.root.update_idletasks()
        self.root.title("BrainDrain Hardware Test")
        # self.root.attributes("-fullscreen", True)

        # Main frame
        frame = tk.Frame(root)
        frame.pack(expand=True)

        self.label = tk.Label(
            frame,
            text="GPIO Status: OFF",
            font=("Arial", 24)
        )
        self.label.pack(pady=20)

        self.button = tk.Button(
            frame,
            text="Toggle GPIO",
            font=("Arial", 20),
            command=self.toggle_gpio,
            width=20,
            height=2
        )
        self.button.pack(pady=20)

        self.exit_button = tk.Button(
            frame,
            text="Exit",
            font=("Arial", 16),
            command=self.shutdown
        )
        self.exit_button.pack(pady=20)

        self.update_ui()

    def toggle_gpio(self):
        return

    def update_ui(self):
        self.root.after(500, self.update_ui)

    def shutdown(self):
        cleanup()


# CLEAN SHUTDOWN

def cleanup(*args):
    global running
    print("Shutting down safely...")

    running = False

    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


# MAIN ENTRY

def test():
    print("Brain Drain starting with motor...")

    # Start GPIO test thread
    thread = threading.Thread(target=gpio_test_loop, daemon=True)
    thread.start()

    # Start Tkinter UI
    root = tk.Tk()
    app = App(root)
    root.mainloop()
