import sys
import signal
import time
from threading import Thread

from gpiozero import LED
from gpiozero.pins.lgpio import LGPIOFactory
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt

# -----------------------
# GPIO SETUP
# -----------------------

# Use lgpio explicitly (Pi 5 safe)
factory = LGPIOFactory()

TEST_PIN = 18
led = LED(TEST_PIN, pin_factory=factory)

gpio_state = False


def gpio_test_loop():
    """
    Background thread toggling GPIO every second
    """
    global gpio_state
    while True:
        gpio_state = not gpio_state
        if gpio_state:
            led.on()
        else:
            led.off()
        time.sleep(1)


# -----------------------
# QT GUI
# -----------------------

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("BrainDrain Hardware Test")
        self.setMinimumSize(800, 480)

        self.label = QLabel("GPIO Status: OFF")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 24px;")

        self.button = QPushButton("Toggle GPIO")
        self.button.setStyleSheet("font-size: 20px; padding: 20px;")
        self.button.clicked.connect(self.toggle_gpio)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)

        # Timer update loop
        self.startTimer(500)

    def toggle_gpio(self):
        global gpio_state
        gpio_state = not gpio_state
        if gpio_state:
            led.on()
        else:
            led.off()

    def timerEvent(self, event):
        if gpio_state:
            self.label.setText("GPIO Status: ON")
        else:
            self.label.setText("GPIO Status: OFF")


# -----------------------
# CLEAN SHUTDOWN
# -----------------------

def cleanup(*args):
    print("Shutting down safely...")
    led.off()
    led.close()
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


# -----------------------
# MAIN ENTRY
# -----------------------

def main():
    print("BrainDrain starting...")

    # Start GPIO test thread
    thread = Thread(target=gpio_test_loop, daemon=True)
    thread.start()

    # Start Qt app
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()  # Good for kiosk mode

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
