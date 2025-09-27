"""
Button Configuration and Handler for Braille Writing Tutor
This module handles all tactile button operations
"""

import RPi.GPIO as GPIO
import time
from typing import Dict, Callable
from pins_config import BUTTON_PINS


class ButtonManager:
    def __init__(self):
        self.buttons = BUTTON_PINS
        self.button_callbacks: Dict[str, Callable] = {}
        self.debounce_delay = 0.2  # 200ms debounce delay
        self.last_press_time = {}
        
        # Initialize GPIO
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Initialize GPIO settings for buttons"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup each button pin
        for button_name, pin in self.buttons.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.last_press_time[button_name] = 0
            
    def register_callback(self, button_name: str, callback: Callable):
        """Register a callback function for a specific button"""
        if button_name in self.buttons:
            self.button_callbacks[button_name] = callback
        else:
            raise ValueError(f"Button '{button_name}' not found in configuration")
            
    def is_button_pressed(self, button_name: str) -> bool:
        """Check if a button is currently pressed (with debouncing)"""
        if button_name not in self.buttons:
            return False
            
        pin = self.buttons[button_name]
        current_time = time.time()
        
        # Check if enough time has passed since last press (debouncing)
        if current_time - self.last_press_time[button_name] < self.debounce_delay:
            return False
            
        # Button is pressed when GPIO reads LOW (pull-up configuration)
        if GPIO.input(pin) == GPIO.LOW:
            self.last_press_time[button_name] = current_time
            return True
            
        return False
        
    def check_all_buttons(self):
        """Check all buttons and execute their callbacks if pressed"""
        for button_name in self.buttons:
            if self.is_button_pressed(button_name):
                callback = self.button_callbacks.get(button_name)
                if callback:
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error executing callback for {button_name}: {e}")
                        
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()


# Button action functions
def on_register_button():
    """Handle register button press"""
    print("Register button pressed - Recording Braille pattern")
    # Add your register logic here
    
    
def on_erase_button():
    """Handle erase button press"""
    print("Erase button pressed - Clearing current input")
    # Add your erase logic here
    
    
def on_read_button():
    """Handle read button press"""
    print("Read button pressed - Reading stored patterns")
    # Add your read logic here
    
    
def on_display_button():
    """Handle display button press"""
    print("Display button pressed - Showing current pattern")
    # Add your display logic here