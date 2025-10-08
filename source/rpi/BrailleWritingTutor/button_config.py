"""
Enhanced Button Configuration for Braille Writing Tutor
Integrates with Phase Manager and Arduino Controller
"""

import RPi.GPIO as GPIO
import time
import threading
from typing import Dict, Callable
from pins_config import BUTTON_PINS, KNOB_PINS
from gtts_config import get_braille_tts


# Singleton instance
_button_manager_instance = None
_button_manager_lock = threading.Lock()


class EnhancedButtonManager:
    def __init__(self):
        self.buttons = BUTTON_PINS
        self.knob_pins = KNOB_PINS
        self.button_callbacks: Dict[str, Callable] = {}
        self.debounce_delay = 0.2  # 200ms debounce delay
        self.last_press_time = {}
        self.running = False
        self.button_threads = []
        self.thread_lock = threading.Lock()
        
        # Knob/rotary encoder state
        self.knob_position = 0
        self.last_clk_state = None
        self.knob_lock = threading.Lock()
        
        # Manager instances (lazy loaded to avoid circular imports)
        self._phase_manager = None
        self._arduino = None
        
        # Initialize GPIO
        self._setup_gpio()
        self._register_default_callbacks()
        
    def _get_phase_manager(self):
        """Lazy load phase manager to avoid circular imports"""
        if self._phase_manager is None:
            from phase_manager import get_phase_manager
            self._phase_manager = get_phase_manager()
        return self._phase_manager
    
    def _get_arduino_controller(self):
        """Lazy load arduino controller to avoid circular imports"""
        if self._arduino is None:
            from arduino_controller import get_arduino_controller
            self._arduino = get_arduino_controller()
        return self._arduino
        
    def _setup_gpio(self):
        """Initialize GPIO settings for buttons and knob"""
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
        
        # Setup knob/rotary encoder pins
        GPIO.setup(self.knob_pins['CLK'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.knob_pins['DT'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.knob_pins['SW'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add knob switch to button tracking
        self.last_press_time['KNOB_SW'] = 0
        
        # Setup knob interrupts
        GPIO.add_event_detect(self.knob_pins['CLK'], GPIO.BOTH, callback=self._handle_knob_rotation)
        GPIO.add_event_detect(self.knob_pins['SW'], GPIO.FALLING, 
                            callback=lambda channel: self._button_interrupt_handler('KNOB_SW'),
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
            # Provide audio feedback for errors
            try:
                tts = get_braille_tts()
                tts.speak("Error sa button operation")
            except:
                pass
    
    def _register_default_callbacks(self):
        """Register default callbacks for all buttons"""
        try:
            self.register_callback('REGISTER', self._handle_register_button)
            self.register_callback('ERASE', self._handle_erase_button)
            self.register_callback('READ', self._handle_read_button)
            self.register_callback('DISPLAY', self._handle_display_button)
            self.register_callback('KNOB_SW', self._handle_knob_button)
        except Exception as e:
            print(f"Error registering default callbacks: {e}")
    
    def _handle_register_button(self):
        """Handle register button press with phase integration"""
        print("Register button pressed")
        try:
            phase_manager = self._get_phase_manager()
            phase_manager.handle_register_button()
        except Exception as e:
            print(f"Error in register button handler: {e}")
    
    def _handle_erase_button(self):
        """Handle erase button press with phase integration"""
        print("Erase button pressed")
        try:
            phase_manager = self._get_phase_manager()
            phase_manager.handle_erase_button()
        except Exception as e:
            print(f"Error in erase button handler: {e}")
    
    def _handle_read_button(self):
        """Handle read button press with phase integration"""
        print("Read button pressed")
        try:
            phase_manager = self._get_phase_manager()
            phase_manager.handle_read_button()
        except Exception as e:
            print(f"Error in read button handler: {e}")
    
    def _handle_display_button(self):
        """Handle display button press with phase integration"""
        print("Display button pressed")
        try:
            phase_manager = self._get_phase_manager()
            phase_manager.handle_display_button()
        except Exception as e:
            print(f"Error in display button handler: {e}")
    
    def _handle_knob_button(self):
        """Handle knob button press (emergency stop/power toggle)"""
        print("Knob button pressed")
        try:
            from phase_manager import TutoringPhases
            phase_manager = self._get_phase_manager()
            current_phase = phase_manager.get_current_phase()
            
            if current_phase == TutoringPhases.OFF:
                # Turn on system - start with Phase 1
                phase_manager.set_phase(TutoringPhases.EMBOSSING)
                self.knob_position = TutoringPhases.EMBOSSING
                tts = get_braille_tts()
                tts.speak("Sistema binuksan. Nagsimula sa Phase 1.")
            else:
                # Emergency stop - turn off system
                phase_manager.set_phase(TutoringPhases.OFF)
                self.knob_position = TutoringPhases.OFF
                tts = get_braille_tts()
                tts.speak("Emergency stop. Sistema naka-off na.")
                
        except Exception as e:
            print(f"Error in knob button handler: {e}")
    
    def _handle_knob_rotation(self, channel):
        """Handle rotary encoder rotation for phase selection"""
        with self.knob_lock:
            clk_state = GPIO.input(self.knob_pins['CLK'])
            dt_state = GPIO.input(self.knob_pins['DT'])
            
            if self.last_clk_state is None:
                self.last_clk_state = clk_state
                return
            
            if clk_state != self.last_clk_state:
                try:
                    if dt_state != clk_state:
                        # Clockwise rotation - next phase
                        self.knob_position += 1
                        direction = "clockwise"
                    else:
                        # Counter-clockwise rotation - previous phase
                        self.knob_position -= 1
                        direction = "counter-clockwise"
                    
                    # Keep position within valid range (0-6 for phases)
                    self.knob_position = max(0, min(6, self.knob_position))
                    
                    print(f"Knob rotated {direction}, position: {self.knob_position}")
                    
                    # Update phase
                    phase_manager = self._get_phase_manager()
                    phase_manager.set_phase(self.knob_position)
                    
                except Exception as e:
                    print(f"Error in knob rotation handler: {e}")
            
            self.last_clk_state = clk_state
    
    def get_knob_position(self) -> int:
        """Get current knob position"""
        return self.knob_position
    
    def set_knob_position(self, position: int):
        """Set knob position (for synchronization)"""
        with self.knob_lock:
            self.knob_position = max(0, min(6, position))
    
    def register_callback(self, button_name: str, callback: Callable):
        """Register a callback function for a specific button"""
        if button_name in self.buttons or button_name == 'KNOB_SW':
            with self.thread_lock:
                self.button_callbacks[button_name] = callback
        else:
            raise ValueError(f"Button '{button_name}' not found in configuration")
            
    def start_monitoring(self):
        """Start the button monitoring system"""
        self.running = True
        print("Enhanced button monitoring started with GPIO interrupts and knob support")
        
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
        try:
            self.stop_monitoring()
            GPIO.cleanup()
            print("GPIO cleanup completed")
        except Exception as e:
            print(f"Error during GPIO cleanup: {e}")


# Legacy button callback functions for backward compatibility
def on_register_button():
    """Legacy register button callback"""
    try:
        tts = get_braille_tts()
        tts.registered()
        print("Register button: Pattern recorded")
    except Exception as e:
        print(f"Error in register button callback: {e}")

def on_erase_button():
    """Legacy erase button callback"""
    try:
        tts = get_braille_tts()
        tts.erased()
        print("Erase button: Input cleared")
    except Exception as e:
        print(f"Error in erase button callback: {e}")

def on_read_button():
    """Legacy read button callback"""
    try:
        tts = get_braille_tts()
        tts.reading_pattern("Walang naka-save na pattern")
        print("Read button: Reading stored pattern")
    except Exception as e:
        print(f"Error in read button callback: {e}")

def on_display_button():
    """Legacy display button callback"""
    try:
        tts = get_braille_tts()
        tts.displaying_pattern("Wala pang i-display")
        print("Display button: Showing pattern on mechanical display")
    except Exception as e:
        print(f"Error in display button callback: {e}")


# Singleton management functions
def get_button_manager() -> EnhancedButtonManager:
    """Get the singleton button manager instance"""
    global _button_manager_instance
    with _button_manager_lock:
        if _button_manager_instance is None:
            _button_manager_instance = EnhancedButtonManager()
        return _button_manager_instance

def cleanup_button_manager():
    """Clean up the button manager singleton"""
    global _button_manager_instance
    with _button_manager_lock:
        if _button_manager_instance is not None:
            _button_manager_instance.cleanup()
            _button_manager_instance = None


# Maintain backward compatibility
ButtonManager = EnhancedButtonManager


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