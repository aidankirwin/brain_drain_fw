import tkinter as tk
from screens.volumewaveform import VolumeWaveform
from screens.icpwaveform import ICPWaveform
from dataCollect import DataBuffer
from motorcontrol import MotorControl
from motor import Motor
from tkinter.font import Font

class App:
    def __init__(self, root):

        # Initial target ICP value
        self.target_icp = 12
        # Initial drainage state — True to match GUI button showing "Stop Drainage" on load
        self.is_draining = True

        print('starting sensor reads')

        # Attach data buffer to app so it can be passed to screens that need it (thread_3)
        self.data_buffer = DataBuffer()
        self.data_buffer.start()

        print('starting motor control')

        # Start motor control thread (thread_4)
        self.motor_control = MotorControl(self.data_buffer, self.target_icp, self.is_draining)
        self.motor_control.start()

        print('starting stepper thread')

        # Start motor thread (thread_5)
        motor = Motor(self.motor_control)
        motor.start()

        # create a popup after 10 seconds to simulate blockage detection
        root.after(2000, self.create_popup)

        print('creating main window')
        # creating the main window
        self.root = root
        self.root.geometry("400x500")
        self.root.configure(bg="white")
        self.root.title("NeuroFlow")
        self.root.attributes("-fullscreen", True)

        # container for switching pages
        self.container = tk.Frame(root, bg="white")
        self.container.pack(fill="both", expand=True)

        self.frames = {}

        # add all screens here
        screens = [
            ICPWaveform,
            VolumeWaveform, 
        ]

        print('starting waveform display')

        # iterate through the screens to stack them (i.e, display the pages in the correct order)
        for ScreenClass in screens:
            if ScreenClass == ICPWaveform:
                frame = ScreenClass(self.container, self, self.data_buffer)
            else:
                frame = ScreenClass(self.container, self, self.data_buffer)
            self.frames[ScreenClass.__name__] = frame
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        print('show icp waveform screen')

        self.show("ICPWaveform")

    def create_popup(self):
        # Main Window Setup
        popup_root = tk.Tk()
        popup_root.title("System Alert")
        popup_root.geometry("500x300")
        popup_root.configure(bg="white")

        # Fonts
        title_font = Font(family="Inter", size=24, weight="normal")
        body_font = Font(family="Inter", size=18, weight="normal")
        button_font = Font(family="Inter", size=16)

        # Main Container
        content_frame = tk.Frame(popup_root, bg="white", padx=40, pady=40)
        content_frame.pack(expand=True, fill="both")

        # Header Row (Title)
        title_label = tk.Label(
            content_frame, 
            text="Blockage Detected", 
            font=title_font, 
            bg="white", 
            fg="black"
        )
        title_label.grid(row=0, column=1, sticky="w", pady=(0, 20))

        # Icon and Message Row
        # Note: Using a simple Unicode character for the red '!' icon
        icon_label = tk.Label(
            content_frame, 
            text="!", 
            font=("Arial", 40, "bold"), 
            fg="#A52A2A", 
            bg="white",
            highlightthickness=3,
            highlightbackground="#A52A2A",
            padx=10
        )
        icon_label.grid(row=1, column=0, rowspan=2, padx=(0, 20), sticky="n")

        message_text = "An obstruction has been detected.\nManually flush the system or\nirrigate."
        message_label = tk.Label(
            content_frame, 
            text=message_text, 
            font=body_font, 
            bg="white", 
            fg="black", 
            justify="left"
        )
        message_label.grid(row=1, column=1, sticky="w")

        # Button Row
        button_frame = tk.Frame(content_frame, bg="white")
        button_frame.grid(row=3, column=1, sticky="e", pady=(30, 0))

        exit_btn = tk.Button(
            button_frame, 
            text="Exit", 
            font=button_font, 
            bg="white", 
            fg="black",
            padx=25, 
            pady=10,
            borderwidth=0.5,
            relief="solid",
            command=popup_root.destroy
        )
        exit_btn.pack(side="left", padx=10)

        def irrigate_and_close():
            self.irrigate()  # Call the irrigate method in the main app
            popup_root.destroy()

        irrigate_btn = tk.Button(
            button_frame,
            text="Irrigate",
            font=button_font,
            bg="#D8E6FA",
            fg="#3D84E7",
            padx=25, 
            pady=10,
            borderwidth=0.5,
            highlightbackground="blue",
            highlightthickness=1,
            command=irrigate_and_close
        )
        irrigate_btn.pack(side="left", padx=10)

        popup_root.mainloop()

    def update_target_icp(self, new_value):
        """Update the target ICP value in MotorControl from GUI."""
        self.target_icp = new_value
        self.motor_control.update_target_icp(new_value)

    def fetch_drainage_state(self, is_draining):
        """Update the drainage state in MotorControl from GUI."""
        self.is_draining = is_draining
        self.motor_control.fetch_drainage_state(is_draining)

    def irrigate(self):
        self.motor_control.is_irrigating = True

    def show(self, screen_name):
        self.frames[screen_name].tkraise()


