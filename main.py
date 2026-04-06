import tkinter as tk
from app import App
from test import test
import signal
import sys

from dataSaver import data_saver, SAVE_DATA

mode = 'DEMO'
# DEMO, MOTOR_TEST, SENSOR_TEST, BATTERY_TEST

def cleanup(*args):
    global running
    print("Shutting down safely...")

    if SAVE_DATA:
        data_saver.update_csv()  # Ensure all data is saved on exit

    running = False
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

if __name__ == "__main__":
    if mode == 'DEMO':
        root = tk.Tk()
        app = App(root)
        root.mainloop()
        
    else:
        test(test_type=mode)