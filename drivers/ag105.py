import RPi.GPIO as GPIO
import board
import busio

class AG105:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.address = 0x30  # I2C address of the AG105 charger

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
            "measured_battery_voltage": 0x05,
            "measured_battery_current": 0x06,
            "measured_supply_voltage": 0x07
        }

    def read_battery_status(self, register_name):
        result = bytearray(2)  # 1 byte for status, 1 byte for data

        if register_name not in self.register_bytes:
            raise ValueError(f"Invalid register name: {register_name}")

        register_byte = self.register_bytes[register_name]

        # Read from the register
        self.i2c.writeto_then_readfrom(self.address, bytes([register_byte]), result)

        # Get the status and data bytes
        status_byte = result[0]
        data_byte = result[1]

        # Get the first 3 bits of the status byte
        shift_amount = status_byte.bit_length() - 3
        first_3_status_bits = status_byte >> shift_amount

        # Interpret the status bits
        status = self.status_bits[first_3_status_bits] if first_3_status_bits in self.status_bits else "unknown_status"

        # Interpret the data byte
        if register_name == "measured_battery_voltage":
            # The data byte represents the battery voltage in 100mV increments
            data = data_byte * 0.064  # Convert to volts
        elif register_name == "measured_battery_current":
            # The data byte represents the battery current in 100mA increments
            data = data_byte * 0.011 # Convert to amps
        elif register_name == "measured_supply_voltage":
            # The data byte represents the supply voltage in 100mV increments
            data = data_byte * 0.141  # Convert to volts
        else:
            data = None

        return data, status