import tkinter as tk
from app import App
from test import test

mode = 'DEMO'
# DEMO, MOTOR_TEST, SENSOR_TEST

if __name__ == "__main__":
    if mode == 'DEMO':
        root = tk.Tk()
        app = App(root)
        root.mainloop()
        
    else:
        test(test_type=mode)