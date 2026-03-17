import sys
import time
import signal
import threading
import tkinter as tk

from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory

from gpiozero import OutputDevice
from time import sleep


def gpio_test_loop():
    STEP_PIN = 3  # BCM numbering
    step = OutputDevice(STEP_PIN)
    delay_time = 0.01  # 10 ms (same as Arduino)

    try:
        while True:
            step.on()
            sleep(0.005)   # HIGH pulse (5 ms)
            step.off()
            sleep(delay_time)

    except KeyboardInterrupt:
        print("Stopped")

# TKINTER UI

class App:
    def __init__(self, root):
        self.root = root
        self.root.update_idletasks()
        self.root.title("BrainDrain Hardware Test")
        self.root.attributes("-fullscreen", True)

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
