"""
Braille Writing Tutor - Main Application
Integrates Phase Manager, Arduino Controller, and Enhanced Button Management
"""

import time
import signal
import sys
import threading
from gtts_config import get_braille_tts, cleanup_tts
from phase_manager import get_phase_manager, cleanup_phase_manager, TutoringPhases
from arduino_controller import get_arduino_controller, cleanup_arduino_controller
from button_config import get_button_manager, cleanup_button_manager


class BrailleWritingTutor:
    def __init__(self):
        """Initialize the Braille Writing Tutor system"""
        print("Initializing Braille Writing Tutor...")
        
        # System state
        self.running = True
        self.initialization_complete = False
        
        # Initialize managers (order matters!)
        try:
            # 1. Initialize TTS first (no dependencies)
            self.tts = get_braille_tts()
            print("✓ TTS system initialized")
            
            # 2. Initialize Arduino controller
            self.arduino = get_arduino_controller()
            print("✓ Arduino controller initialized")
            
            # 3. Initialize phase manager (depends on TTS and Arduino)
            self.phase_manager = get_phase_manager()
            print("✓ Phase manager initialized")
            
            # 4. Initialize button manager (depends on phase manager)
            self.button_manager = get_button_manager()
            print("✓ Button manager initialized")
            
            # 5. Setup signal handlers for clean shutdown
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            self.initialization_complete = True
            print("✓ All systems initialized successfully")
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            self.shutdown()
            raise
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.shutdown()
        
    def run(self):
        """Main application loop"""
        if not self.initialization_complete:
            print("System not properly initialized. Cannot start.")
            return
            
        print("\n" + "="*50)
        print("    BRAILLE WRITING TUTOR - SISTEMA AKTIBO")
        print("="*50)
        print()
        print("Phase Control:")
        print("- I-rotate ang knob para magpalit ng phase (0-6)")
        print("- Phase 0: Sistema nakasara")
        print("- Phase 1: Pag-aaral ng basic dots")
        print("- Phase 2: Pag-aaral ng mga titik")
        print("- Phase 3: Pag-aaral ng mga salita")
        print("- Phase 4: Pag-aaral ng pangungusap")
        print("- Phase 5: Larong pang-edukasyon")
        print("- Phase 6: Libreng pagsusulat")
        print()
        print("Button Functions:")
        print("- REGISTER: I-save ang pattern/input")
        print("- ERASE: Burahin ang input")
        print("- READ: Basahin ang naka-store")
        print("- DISPLAY: Ipakita sa mechanical display")
        print()
        print("Press Ctrl+C to exit")
        print("-" * 50)
        
        # Start monitoring systems
        try:
            # Start Arduino communication
            self.arduino.start()
            print("✓ Arduino communication started")
            
            # Start button monitoring
            self.button_manager.start_monitoring()
            print("✓ Button monitoring started")
            
            # Initial system state
            self.phase_manager.set_phase(TutoringPhases.OFF)
            
            # Play welcome message
            self.tts.welcome()
            time.sleep(2)
            
            # Announce initial instructions
            self.tts.speak("Maligayang pagdating sa Braille Writing Tutor!")
            time.sleep(1)
            self.tts.speak("I-rotate ang knob para pumili ng phase. Nagsisimula tayo sa Phase 0 - sistema nakasara.")
            
            # Main application loop
            self._main_loop()
            
        except Exception as e:
            print(f"Runtime error: {e}")
        finally:
            self.shutdown()
    
    def _main_loop(self):
        """Main application loop with system monitoring"""
        last_status_check = time.time()
        status_interval = 30  # Check system status every 30 seconds
        
        while self.running:
            current_time = time.time()
            
            # Periodic system status check
            if current_time - last_status_check > status_interval:
                self._check_system_status()
                last_status_check = current_time
            
            # Check for Arduino connection
            if not self.arduino.is_connected():
                print("Warning: Arduino connection lost")
                # Attempt reconnection
                try:
                    self.arduino.reconnect()
                    if self.arduino.is_connected():
                        print("✓ Arduino reconnected")
                        self.tts.speak("Arduino reconnected")
                except Exception as e:
                    print(f"Arduino reconnection failed: {e}")
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
    
    def _check_system_status(self):
        """Periodic system status check"""
        try:
            current_phase = self.phase_manager.get_current_phase()
            knob_position = self.button_manager.get_knob_position()
            arduino_connected = self.arduino.is_connected()
            
            print(f"Status - Phase: {current_phase}, Knob: {knob_position}, Arduino: {'✓' if arduino_connected else '✗'}")
            
            # Sync knob position with phase if they're out of sync
            if knob_position != current_phase:
                print(f"Syncing knob position {knob_position} with phase {current_phase}")
                self.button_manager.set_knob_position(current_phase)
                
        except Exception as e:
            print(f"Error in system status check: {e}")
    
    def shutdown(self):
        """Clean shutdown of the application"""
        print("\nInitiating system shutdown...")
        
        try:
            # Set system to OFF phase
            if hasattr(self, 'phase_manager') and self.phase_manager:
                self.phase_manager.set_phase(TutoringPhases.OFF)
            
            # Play shutdown message
            if hasattr(self, 'tts') and self.tts:
                self.tts.shutdown_message()
                time.sleep(2)  # Give time for audio to play
            
            self.running = False
            
            # Clean up in reverse order of initialization
            cleanup_button_manager()
            print("✓ Button manager cleaned up")
            
            cleanup_phase_manager()
            print("✓ Phase manager cleaned up")
            
            cleanup_arduino_controller()
            print("✓ Arduino controller cleaned up")
            
            cleanup_tts()
            print("✓ TTS system cleaned up")
            
            print("✓ System shutdown complete")
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
        
        sys.exit(0)


def main():
    """Main entry point"""
    try:
        print("Starting Braille Writing Tutor...")
        tutor = BrailleWritingTutor()
        tutor.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
