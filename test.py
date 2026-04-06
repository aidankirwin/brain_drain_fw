import sys
import time
import signal
import threading
import tkinter as tk

from gpiozero import OutputDevice
from time import sleep

import adafruit_ads1x15.ads1115 as ADS
import board
import busio

import time
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice, AngularServo

import pickle
import matplotlib.pyplot as plt

def sensor_test_loop():
    period = 0.0033  # ~300 Hz
    lc_scale = 0.32830703
    lc_offset = -1634.5324180655623
    with open('model.pkl', 'rb') as handle:
            loaded_model = pickle.load(handle)

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c)
    ads.data_rate = 860

def battery_test_loop():
    pin = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # make a realtime plot of the battery status pin, sample the value every 10 ms
    # make sure plot is non-blocking and updates in real time

    plt.ion()
    fig, ax = plt.subplots()
    xdata, ydata = [], []
    line, = ax.plot(xdata, ydata)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Battery Status Pin')
    ax.set_title('Battery Status Pin Over Time')

    try:
        while True:
            print(GPIO.input(pin))
            xdata.append(time.time())
            ydata.append(GPIO.input(pin))
            line.set_xdata(xdata)
            line.set_ydata(ydata)
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            time.sleep(0.001)
    except KeyboardInterrupt:
        GPIO.cleanup()

def motor_test_loop():

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
    servo = AngularServo(servo_pin, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0025)
    servo.detach()

    # Delay settings
    delay_time = 0.05  # 10 ms

    try:
        while True:

            # --- Motor ON loop ---
            # for i in range(2):
            #     print("dc motor start")
            #     motor.value = 200/255.0  # Convert Arduino PWM (0–255) to 0–1
            #     time.sleep(1)

            # # --- Motor OFF loop ---
            # for i in range(1):
            #     print("dc motor stop")
            #     motor.value = 0
            #     time.sleep(1)

            # time.sleep(2)

            # --- Stepper pulse loop ---
            for i in range(1000):
                print("stepper motor")
                GPIO.output(step_pin, GPIO.HIGH)
                time.sleep(0.005)
                GPIO.output(step_pin, GPIO.LOW)
                time.sleep(delay_time)

            # --- Servo movement ---
            # time.sleep(2)
            # for i in range(2):
            #     print('servo move')
            #     servo.angle = 0
            #     time.sleep(4)
            #     servo.angle = 180
            #     time.sleep(4)

            # Optional: "detach" equivalent (stop sending signal)
            # servo.detach()
            # time.sleep(4)

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

        # self.exit_button = tk.Button(
        #     frame,
        #     text="Exit",
        #     font=("Arial", 16),
        #     command=self.shutdown
        # )
        # self.exit_button.pack(pady=20)

        self.update_ui()

    def toggle_gpio(self):
        return

    def update_ui(self):
        self.root.after(500, self.update_ui)


# MAIN ENTRY

def test(test_type='MOTOR_TEST'):
    print("Brain Drain starting with motor...")

    if test_type == 'MOTOR_TEST':
        thread = threading.Thread(target=motor_test_loop, daemon=True)
        thread.start()
    elif test_type == 'SENSOR_TEST':
        thread = threading.Thread(target=motor_test_loop, daemon=True)
        thread.start()
    elif test_type == 'BATTERY_TEST':
        thread = threading.Thread(target=battery_test_loop, daemon=True)
        thread.start()

    # Start Tkinter UI
    root = tk.Tk()
    app = App(root)
    root.mainloop()
