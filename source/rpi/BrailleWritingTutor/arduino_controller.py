"""
Arduino Communication Module for Braille Writing Tutor
Handles serial communication with Arduino Uno (Braille Display Controller)
"""

import serial
import threading
import time
import queue
from typing import Optional, Callable


class ArduinoController:
    """Manages communication with Arduino Uno Braille Display Controller"""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud_rate: int = 115200):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.running = False
        
        # Message queues
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Threading
        self.reader_thread: Optional[threading.Thread] = None
        self.writer_thread: Optional[threading.Thread] = None
        self.thread_lock = threading.Lock()
        
        # Callbacks for different message types
        self.callbacks = {
            'READY': None,
            'PHASE_SET': None,
            'DISPLAYED': None,
            'BUTTON_PRESS': None,
            'BUTTON_RELEASE': None,
            'DOT_PRESSED': None,
            'HEARTBEAT': None,
            'ERROR': None
        }
        
        # Current system state
        self.current_phase = 0
        self.display_enabled = False
        self.last_heartbeat = time.time()
        
    def connect(self) -> bool:
        """Connect to Arduino"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,
                write_timeout=1
            )
            
            # Wait for Arduino to initialize
            time.sleep(2)
            
            # Check if Arduino is ready
            if self.serial_connection.is_open:
                self.is_connected = True
                self.running = True
                
                # Start communication threads
                self.start_threads()
                
                print(f"Connected to Arduino on {self.port}")
                return True
            else:
                print(f"Failed to open serial port {self.port}")
                return False
                
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error connecting to Arduino: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.running = False
        
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2)
        
        if self.writer_thread and self.writer_thread.is_alive():
            self.writer_thread.join(timeout=2)
            
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            
        self.is_connected = False
        print("Disconnected from Arduino")
    
    def start_threads(self):
        """Start reader and writer threads"""
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        
        self.reader_thread.start()
        self.writer_thread.start()
    
    def _reader_loop(self):
        """Read messages from Arduino"""
        while self.running and self.is_connected:
            try:
                if self.serial_connection and self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line:
                        self._process_message(line)
                        
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
            except Exception as e:
                print(f"Reader error: {e}")
                break
    
    def _writer_loop(self):
        """Send commands to Arduino"""
        while self.running and self.is_connected:
            try:
                # Get command from queue (with timeout)
                try:
                    command = self.command_queue.get(timeout=0.1)
                    if self.serial_connection and self.serial_connection.is_open:
                        self.serial_connection.write(f"{command}\n".encode('utf-8'))
                        self.serial_connection.flush()
                    self.command_queue.task_done()
                except queue.Empty:
                    continue
                    
            except Exception as e:
                print(f"Writer error: {e}")
                break
    
    def _process_message(self, message: str):
        """Process incoming message from Arduino"""
        try:
            # Parse message type
            if ':' in message:
                msg_type, msg_data = message.split(':', 1)
            else:
                msg_type = message
                msg_data = ""
            
            # Update system state based on message
            if msg_type == "READY":
                print("Arduino is ready")
                
            elif msg_type == "PHASE_SET":
                self.current_phase = int(msg_data)
                print(f"Phase set to: {self.current_phase}")
                
            elif msg_type == "DISPLAYED":
                print(f"Displayed text: {msg_data}")
                
            elif msg_type == "MIRRORED":
                print(f"Displayed mirrored text: {msg_data}")
                
            elif msg_type == "BUTTON_PRESS":
                self._handle_button_press(msg_data)
                
            elif msg_type == "BUTTON_RELEASE":
                self._handle_button_release(msg_data)
                
            elif msg_type == "DOT_PRESSED":
                self._handle_dot_press(msg_data)
                
            elif msg_type == "HEARTBEAT":
                self.last_heartbeat = time.time()
                
            elif msg_type == "ERROR":
                print(f"Arduino error: {msg_data}")
                
            # Call registered callback if available
            callback = self.callbacks.get(msg_type)
            if callback:
                callback(msg_data)
                
        except Exception as e:
            print(f"Error processing message '{message}': {e}")
    
    def _handle_button_press(self, data: str):
        """Handle button press from writing slate"""
        try:
            parts = data.split(',')
            if len(parts) >= 4:
                row, col, cell, dot = map(int, parts)
                print(f"Button pressed: row={row}, col={col}, cell={cell}, dot={dot}")
                
                # Call callback if registered
                callback = self.callbacks.get('BUTTON_PRESS')
                if callback:
                    callback(row, col, cell, dot)
                    
        except Exception as e:
            print(f"Error handling button press: {e}")
    
    def _handle_button_release(self, data: str):
        """Handle button release from writing slate"""
        try:
            parts = data.split(',')
            if len(parts) >= 4:
                row, col, cell, dot = map(int, parts)
                print(f"Button released: row={row}, col={col}, cell={cell}, dot={dot}")
                
                # Call callback if registered
                callback = self.callbacks.get('BUTTON_RELEASE')
                if callback:
                    callback(row, col, cell, dot)
                    
        except Exception as e:
            print(f"Error handling button release: {e}")
    
    def _handle_dot_press(self, data: str):
        """Handle dot press in embossing phase"""
        try:
            parts = data.split(',')
            if len(parts) >= 2:
                cell, dot = map(int, parts)
                print(f"Dot pressed: cell={cell}, dot={dot}")
                
                # Call callback if registered
                callback = self.callbacks.get('DOT_PRESSED')
                if callback:
                    callback(cell, dot)
                    
        except Exception as e:
            print(f"Error handling dot press: {e}")
    
    # Command methods
    def set_phase(self, phase: int):
        """Set tutoring phase"""
        self.send_command(f"PHASE:{phase}")
    
    def display_text(self, text: str):
        """Display text on Braille display"""
        self.send_command(f"DISPLAY:{text}")
    
    def display_mirrored_text(self, text: str):
        """Display mirrored text for writing practice"""
        self.send_command(f"MIRROR:{text}")
    
    def clear_display(self):
        """Clear Braille display"""
        self.send_command("CLEAR")
    
    def enable_display(self):
        """Enable Braille display"""
        self.send_command("ENABLE")
        self.display_enabled = True
    
    def disable_display(self):
        """Disable Braille display"""
        self.send_command("DISABLE")
        self.display_enabled = False
    
    def run_test(self):
        """Run Arduino test sequence"""
        self.send_command("TEST")
    
    def get_status(self):
        """Request status from Arduino"""
        self.send_command("STATUS")
    
    def send_command(self, command: str):
        """Send command to Arduino"""
        if self.is_connected:
            self.command_queue.put(command)
        else:
            print(f"Cannot send command - not connected: {command}")
    
    def register_callback(self, message_type: str, callback: Callable):
        """Register callback for specific message type"""
        if message_type in self.callbacks:
            self.callbacks[message_type] = callback
        else:
            print(f"Unknown message type: {message_type}")
    
    def start(self):
        """Start Arduino communication"""
        return self.connect()
    
    def reconnect(self):
        """Reconnect to Arduino"""
        print("Attempting to reconnect to Arduino...")
        self.disconnect()
        time.sleep(1)
        return self.connect()
    
    def is_connected(self) -> bool:
        """Check if Arduino is connected and responsive"""
        if not self.is_connected:
            return False
        # Check heartbeat
        return self.is_arduino_alive()


# Singleton management (updated)
_arduino_controller_instance = None
_arduino_controller_lock = threading.Lock()

def get_arduino_controller() -> ArduinoController:
    """Get the singleton Arduino controller instance"""
    global _arduino_controller_instance
    with _arduino_controller_lock:
        if _arduino_controller_instance is None:
            _arduino_controller_instance = ArduinoController()
        return _arduino_controller_instance

def cleanup_arduino_controller():
    """Clean up the Arduino controller singleton"""
    global _arduino_controller_instance
    with _arduino_controller_lock:
        if _arduino_controller_instance is not None:
            _arduino_controller_instance.disconnect()
            _arduino_controller_instance = None

# Maintain backward compatibility
def cleanup_arduino():
    """Legacy cleanup function"""
    cleanup_arduino_controller()