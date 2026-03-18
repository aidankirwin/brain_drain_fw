import tkinter as tk
from screens.volumewaveform import VolumeWaveform
from screens.icpwaveform import ICPWaveform
from dataCollect import DataBuffer
from motorcontrol import MotorControl
from motor import Motor

class App:
    def __init__(self, root):

        # Initial target ICP value
        self.target_icp = 15

        # Attach data buffer to app so it can be passed to screens that need it (thread_3)
        self.data_buffer = DataBuffer(self.sensor_read)
        self.data_buffer.start()

        # Start motor control thread (thread_4)
        self.motor_control = MotorControl(self.data_buffer, self.target_icp)
        self.motor_control.start()

        # Start motor thread (thread_5)
        # motor = Motor(self.motor_control)
        # motor.start()

        # creating the main window
        self.root = root
        self.root.geometry("400x500")
        self.root.configure(bg="white")
        self.root.title("NeuroFlow")

        # container for switching pages
        self.container = tk.Frame(root, bg="white")
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # add all screens here
        screens = [
            ICPWaveform,
            VolumeWaveform, 
        ]

        # iterate through the screens to stack them (i.e, display the pages in the correct order)
        for ScreenClass in screens:
            if ScreenClass == ICPWaveform:
                frame = ScreenClass(self.container, self, self.data_buffer)
            else:
                frame = ScreenClass(self.container, self)
            self.frames[ScreenClass.__name__] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show("ICPWaveform")

    def update_target_icp(self, new_value):
        """Update the target ICP value in MotorControl from GUI."""
        self.motor_control.update_target_icp(new_value)

    def show(self, screen_name):
        self.frames[screen_name].tkraise()


