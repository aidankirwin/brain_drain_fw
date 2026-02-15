from gpiozero import DigitalOutputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device
import time

Device.pin_factory = LGPIOFactory()

print('Hello world!')

led = DigitalOutputDevice(18)  # Replace with your GPIO pin
led.on()
time.sleep(2)
led.off()