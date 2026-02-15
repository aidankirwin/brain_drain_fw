from gpiozero import DigitalOutputDevice
import time

print('Hello world!')

led = DigitalOutputDevice(18)  # Replace with your GPIO pin
led.on()
time.sleep(2)
led.off()