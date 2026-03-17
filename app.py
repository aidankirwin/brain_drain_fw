import tkinter as tk
from screens.volumewaveform import VolumeWaveform
from screens.icpwaveform import ICPWaveform
from dataBuffer import DataBuffer

class App:
    def __init__(self, root):
        # Attach the data buffer to the app so it can be passed to screens that need it (e.g., ICPWaveform)
        self.data_buffer = DataBuffer()
        self.data_buffer.start()  # Start the data buffer to collect sensor data

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

    def show(self, screen_name):
        self.frames[screen_name].tkraise()


