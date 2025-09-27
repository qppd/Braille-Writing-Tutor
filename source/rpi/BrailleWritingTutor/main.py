"""
Braille Writing Tutor - Main Application
This is the main application file for the Braille Writing Tutor system
"""

import time
import signal
import sys
from button_config import (
    ButtonManager, 
    on_register_button, 
    on_erase_button, 
    on_read_button, 
    on_display_button
)


class BrailleWritingTutor:
    def __init__(self):
        """Initialize the Braille Writing Tutor system"""
        self.button_manager = ButtonManager()
        self.running = True
        
        # Register button callbacks
        self.setup_button_callbacks()
        
        # Setup signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def setup_button_callbacks(self):
        """Setup callbacks for all tactile buttons"""
        self.button_manager.register_callback('register', on_register_button)
        self.button_manager.register_callback('erase', on_erase_button)
        self.button_manager.register_callback('read', on_read_button)
        self.button_manager.register_callback('display', on_display_button)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.shutdown()
        
    def run(self):
        """Main application loop"""
        print("Braille Writing Tutor started")
        print("Press Ctrl+C to exit")
        print("Available buttons:")
        print("- Register: Record Braille pattern")
        print("- Erase: Clear current input") 
        print("- Read: Read stored patterns")
        print("- Display: Show current pattern")
        print("-" * 40)
        
        # Start button monitoring with threading
        self.button_manager.start_monitoring()
        
        try:
            while self.running:
                # Main application logic can go here
                # Buttons are now handled asynchronously via interrupts
                
                # You can add other tasks here that run periodically
                # For now, just keep the main thread alive
                time.sleep(0.1)  # 100ms delay - much less CPU intensive
                
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Clean shutdown of the application"""
        print("Cleaning up GPIO and shutting down...")
        self.running = False
        self.button_manager.cleanup()
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        tutor = BrailleWritingTutor()
        tutor.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Failed to start application: {e}")


if __name__ == '__main__':
    main()
