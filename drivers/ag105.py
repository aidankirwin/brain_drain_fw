import RPi.GPIO as GPIO
import board
import busio

class AG105:
    def __init__(self):
        # Initialize I2C communication
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.address = 0x30  # I2C address of the AG105 charger

        # The status pin is connected to GPIO pin 17 and is used to detect changes in the battery status
        self.status_pin = 17
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.status_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.remove_event_detect(17)
        GPIO.add_event_detect(self.status_pin, GPIO.RISING, callback=self.status_change_callback, bouncetime=200)

        # every I2C read involves the following:
        # - module address (0x30)
        # - register addres (1 byte)
        # - module address byte + 1
        # - 1 status byte
        # - 1 data byte

        # the first 0-2 bits of the status byte indicate general status
        self.status_bits = {
            0: "battery_disconnect",
            1: "low_power",
            2: "charging",
            3: "fully_charged",
            4: "bring_up_charge",
            5: "regulation_error",
            6: "thermal_shutdown",
            7: "timeout_error"
        }

        self.register_bytes = {
            "charge_current_setting": 0x00,
            "charge_voltage_setting": 0x01,
            "measured_battery_voltage": 0x05,
            "measured_battery_current": 0x06,
            "measured_supply_voltage": 0x07
        }

        self.charge_voltage_settings = {
            0: 4.2,
            1: 3.9,
            2: 4.0,
            3: 4.1,
            4: 4.2,
            5: 7.8,
            6: 8.0,
            7: 8.2,
            8: 8.4,
            9: 11.7,
            10: 12.0,
            11: 12.3,
            12: 12.6
        }

        self.charge_current_settings = {
            12: 100,
            11: 150,
            10: 200,
            9: 250,
            8: 500,
            7: 750,
            6: 1000,
            5: 1250,
            4: 1500,
            3: 1750,
            2: 2000,
            1: 2250,
            0: 1000
        }

        # on startup, set the charge voltage to 12.6 V
        self.write_raw(self.register_bytes["charge_voltage_setting"], 12)  # Set to 12.6 V

    def status_change_callback(self):
        # report pulses on the status pin
        print("Battery status pulse detected")

    def read_status_pin(self):
        return GPIO.input(self.status_pin)

    def read_raw(self, register_byte):
        result = bytearray(2)
        self.i2c.writeto(self.address, bytes([register_byte]))
        self.i2c.readfrom_into(self.address, result)
        print(f"RAW: {[hex(b) for b in result]}")
        return result
    
    def write_raw(self, register_byte, data_byte):
        self.i2c.writeto(self.address, bytes([register_byte, data_byte]))

    def read_battery_status(self, register_name):
        if register_name not in self.register_bytes:
            raise ValueError(f"Invalid register name: {register_name}")

        register_byte = self.register_bytes[register_name]

        # Read from the register
        result = self.read_raw(register_byte)

        # Get the status and data bytes
        status_byte = result[0]
        data_byte = result[1]

        # Get the first 3 bits of the status byte
        first_3_status_bits = status_byte & 0x07

        # Interpret the status bits
        status = self.status_bits[first_3_status_bits] if first_3_status_bits in self.status_bits else "unknown_status"

        # Interpret the data byte
        if register_name == "measured_battery_voltage":
            data = data_byte * 0.064  # Convert to volts
        elif register_name == "measured_battery_current":
            data = data_byte * 0.011 # Convert to amps
        elif register_name == "measured_supply_voltage":
            data = data_byte * 0.141  # Convert to volts
        elif register_name == "charge_current_setting":
            data = self.charge_current_settings.get(data_byte, None)
        elif register_name == "charge_voltage_setting":
            data = self.charge_voltage_settings.get(data_byte, None)
        else:
            data = None

        return data, status