"""
Pin Configuration for Braille Writing Tutor
This file defines all GPIO pin assignments for the Raspberry Pi
"""

# Button GPIO Pins (BCM numbering)
BUTTON_PINS = {
    'REGISTER': 18,   # GPIO 18 - Register button
    'ERASE': 19,      # GPIO 19 - Erase button  
    'READ': 20,       # GPIO 20 - Read button
    'DISPLAY': 21     # GPIO 21 - Display button
}

# Rotary encoder (knob) pins
KNOB_PINS = {
    'CLK': 22,        # GPIO 22 - Rotary encoder CLK
    'DT': 23,         # GPIO 23 - Rotary encoder DT
    'SW': 24          # GPIO 24 - Rotary encoder switch (push button)
}

# Status LED pins
LED_PINS = {
    'STATUS': 16,     # GPIO 16 - System status LED
    'ERROR': 12,      # GPIO 12 - Error indicator LED
    'PHASE_1': 5,     # GPIO 5 - Phase 1 indicator
    'PHASE_2': 6,     # GPIO 6 - Phase 2 indicator
    'PHASE_3': 13,    # GPIO 13 - Phase 3 indicator
    'PHASE_4': 26     # GPIO 26 - Phase 4 indicator
}

# UART/Serial pins for Arduino communication
SERIAL_PINS = {
    'TX': 14,         # GPIO 14 (TXD) - Serial transmit to Arduino
    'RX': 15          # GPIO 15 (RXD) - Serial receive from Arduino
}

# Alternative USB serial device path
USB_SERIAL_DEVICE = '/dev/ttyUSB0'  # Primary Arduino connection
USB_SERIAL_DEVICE_ALT = '/dev/ttyACM0'  # Alternative Arduino connection

# I2C pins (if needed for additional sensors)
I2C_PINS = {
    'SDA': 2,         # GPIO 2 - I2C Data
    'SCL': 3          # GPIO 3 - I2C Clock
}

# SPI pins (if needed for additional hardware)
SPI_PINS = {
    'MOSI': 10,       # GPIO 10 - SPI Master Out Slave In
    'MISO': 9,        # GPIO 9 - SPI Master In Slave Out
    'SCLK': 11,       # GPIO 11 - SPI Clock
    'CE0': 8,         # GPIO 8 - SPI Chip Enable 0
    'CE1': 7          # GPIO 7 - SPI Chip Enable 1
}

# PWM pins (for potential servo control or brightness control)
PWM_PINS = {
    'PWM0': 18,       # GPIO 18 - PWM channel 0 (shared with REGISTER button)
    'PWM1': 19        # GPIO 19 - PWM channel 1 (shared with ERASE button)
}

# Interrupt-capable pins (for high-priority inputs)
INTERRUPT_PINS = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26]

# All configured pins for reference and validation
ALL_CONFIGURED_PINS = {
    **BUTTON_PINS,
    **KNOB_PINS,
    **LED_PINS,
    **SERIAL_PINS,
    **I2C_PINS,
    **SPI_PINS
}

def validate_pin_configuration():
    """Validate that no pins are double-assigned"""
    used_pins = []
    conflicts = []
    
    for category, pins in [
        ('BUTTON', BUTTON_PINS),
        ('KNOB', KNOB_PINS),
        ('LED', LED_PINS),
        ('SERIAL', SERIAL_PINS),
        ('I2C', I2C_PINS),
        ('SPI', SPI_PINS)
    ]:
        for name, pin in pins.items():
            if pin in used_pins:
                conflicts.append(f"Pin {pin} used in both {category} and previous category")
            used_pins.append(pin)
    
    if conflicts:
        print("Pin configuration conflicts found:")
        for conflict in conflicts:
            print(f"  - {conflict}")
        return False
    else:
        print(f"Pin configuration validated: {len(used_pins)} pins configured")
        return True

def get_available_pins():
    """Get list of available GPIO pins not currently configured"""
    all_gpio_pins = list(range(2, 28))  # GPIO 2-27 are available on RPi
    used_pins = list(ALL_CONFIGURED_PINS.values())
    available = [pin for pin in all_gpio_pins if pin not in used_pins]
    return available

# Pin configuration metadata
PIN_DESCRIPTIONS = {
    18: "Register button / PWM0",
    19: "Erase button / PWM1", 
    20: "Read button",
    21: "Display button",
    22: "Knob CLK",
    23: "Knob DT",
    24: "Knob switch",
    16: "Status LED",
    12: "Error LED",
    5: "Phase 1 LED",
    6: "Phase 2 LED", 
    13: "Phase 3 LED",
    26: "Phase 4 LED",
    14: "Serial TX to Arduino",
    15: "Serial RX from Arduino",
    2: "I2C SDA",
    3: "I2C SCL",
    10: "SPI MOSI",
    9: "SPI MISO",
    11: "SPI SCLK",
    8: "SPI CE0",
    7: "SPI CE1"
}