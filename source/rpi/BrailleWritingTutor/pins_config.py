"""
Pin Configuration for Braille Writing Tutor
This file defines all GPIO pin assignments for the Raspberry Pi
"""

# Button GPIO Pins (BCM numbering)
BUTTON_PINS = {
    'register': 18,   # GPIO 18 - Register button
    'erase': 19,      # GPIO 19 - Erase button  
    'read': 20,       # GPIO 20 - Read button
    'display': 21     # GPIO 21 - Display button
}

# Additional GPIO pins can be added here as needed
# Example:
# LED_PINS = {
#     'status': 16,
#     'error': 12
# }

# UART/Serial pins for Arduino communication
# UART_TX = 14  # GPIO 14 (TXD)
# UART_RX = 15  # GPIO 15 (RXD)