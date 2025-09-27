"""
Button Configuration and Handler for Braille Writing Tutor
This module handles all tactile button operations using threading
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Dict, Callable
from pins_config import BUTTON_PINS
from gtts_config import get_braille_tts


class ButtonManager:
    def __init__(self):
        self.buttons = BUTTON_PINS
        self.button_callbacks: Dict[str, Callable] = {}
        self.debounce_delay = 0.2  # 200ms debounce delay
        self.last_press_time = {}
        self.running = False
        self.button_threads = []
        self.thread_lock = threading.Lock()
        
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
            
        # Setup GPIO interrupt callbacks for each button
        for button_name, pin in self.buttons.items():
            GPIO.add_event_detect(pin, GPIO.FALLING, 
                                callback=lambda channel, name=button_name: self._button_interrupt_handler(name),
                                bouncetime=int(self.debounce_delay * 1000))
            
    def _button_interrupt_handler(self, button_name: str):
        """GPIO interrupt handler for button presses"""
        current_time = time.time()
        
        # Thread-safe debouncing check
        with self.thread_lock:
            if current_time - self.last_press_time[button_name] < self.debounce_delay:
                return
            self.last_press_time[button_name] = current_time
        
        # Execute callback in a separate thread to avoid blocking
        callback = self.button_callbacks.get(button_name)
        if callback:
            thread = threading.Thread(
                target=self._execute_callback,
                args=(button_name, callback),
                daemon=True
            )
            thread.start()
    
    def _execute_callback(self, button_name: str, callback: Callable):
        """Execute button callback in a separate thread"""
        try:
            callback()
        except Exception as e:
            print(f"Error executing callback for {button_name}: {e}")
    
    def register_callback(self, button_name: str, callback: Callable):
        """Register a callback function for a specific button"""
        if button_name in self.buttons:
            with self.thread_lock:
                self.button_callbacks[button_name] = callback
        else:
            raise ValueError(f"Button '{button_name}' not found in configuration")
            
    def start_monitoring(self):
        """Start the button monitoring system"""
        self.running = True
        print("Button monitoring started with GPIO interrupts")
        
    def stop_monitoring(self):
        """Stop the button monitoring system"""
        self.running = False
        
        # Wait for any running callback threads to complete
        for thread in threading.enumerate():
            if thread != threading.current_thread() and thread.daemon:
                thread.join(timeout=1.0)
        
        print("Button monitoring stopped")
    
    def is_button_pressed(self, button_name: str) -> bool:
        """Check if a button is currently pressed (manual check)"""
        if button_name not in self.buttons:
            return False
            
        pin = self.buttons[button_name]
        # Button is pressed when GPIO reads LOW (pull-up configuration)
        return GPIO.input(pin) == GPIO.LOW
                        
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop_monitoring()
        
        # Remove GPIO event detection
        for button_name, pin in self.buttons.items():
            try:
                GPIO.remove_event_detect(pin)
            except Exception:
                pass  # Ignore errors during cleanup
                
        GPIO.cleanup()


# Button action functions (executed in separate threads)
def on_register_button():
    """Handle register button press"""
    thread_id = threading.current_thread().ident
    print(f"[Thread {thread_id}] Register button pressed - Recording Braille pattern")
    
    # Get TTS instance and provide audio feedback
    tts = get_braille_tts()
    tts.button_registered()
    
    # Simulate some processing time
    time.sleep(0.1)
    print(f"[Thread {thread_id}] Register operation completed")
    # Add your register logic here
    
    
def on_erase_button():
    """Handle erase button press"""
    thread_id = threading.current_thread().ident
    print(f"[Thread {thread_id}] Erase button pressed - Clearing current input")
    
    # Get TTS instance and provide audio feedback
    tts = get_braille_tts()
    tts.pattern_erased()
    
    # Simulate some processing time
    time.sleep(0.1)
    print(f"[Thread {thread_id}] Erase operation completed")
    # Add your erase logic here
    
    
def on_read_button():
    """Handle read button press"""
    thread_id = threading.current_thread().ident
    print(f"[Thread {thread_id}] Read button pressed - Reading stored patterns")
    
    # Get TTS instance and provide audio feedback
    tts = get_braille_tts()
    tts.reading_pattern("Sample pattern A")  # Replace with actual pattern data
    
    # Simulate some processing time
    time.sleep(0.1)
    print(f"[Thread {thread_id}] Read operation completed")
    # Add your read logic here
    
    
def on_display_button():
    """Handle display button press"""
    thread_id = threading.current_thread().ident
    print(f"[Thread {thread_id}] Display button pressed - Showing current pattern")
    
    # Get TTS instance and provide audio feedback
    tts = get_braille_tts()
    tts.displaying_pattern()
    
    # Simulate some processing time
    time.sleep(0.1)
    print(f"[Thread {thread_id}] Display operation completed")
    # Add your display logic here