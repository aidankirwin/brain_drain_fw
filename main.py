import sys
import time
import signal
import threading
import tkinter as tk

from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory

# -----------------------
# GPIO SETUP
# -----------------------

factory = LGPIOFactory()

TEST_PIN = 17
led = LED(TEST_PIN, pin_factory=factory)

gpio_state = False
running = True


def gpio_test_loop():
    """
    Background thread toggles GPIO every second
    """
    global gpio_state, running
    while running:
        gpio_state = not gpio_state
        if gpio_state:
            led.on()
        else:
            led.off()
        time.sleep(1)


# -----------------------
# TKINTER UI
# -----------------------

class App:
    def __init__(self, root):
        self.root = root
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
        global gpio_state
        gpio_state = not gpio_state
        if gpio_state:
            led.on()
        else:
            led.off()

    def update_ui(self):
        if gpio_state:
            self.label.config(text="GPIO Status: ON")
        else:
            self.label.config(text="GPIO Status: OFF")

        self.root.after(500, self.update_ui)

    def shutdown(self):
        cleanup()


# -----------------------
# CLEAN SHUTDOWN
# -----------------------

def cleanup(*args):
    global running
    print("Shutting down safely...")

    running = False
    led.off()
    led.close()

    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


# -----------------------
# MAIN ENTRY
# -----------------------

def main():
    print("Brain Drain starting...")

    # Start GPIO test thread
    thread = threading.Thread(target=gpio_test_loop, daemon=True)
    thread.start()

    # Start Tkinter UI
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
