"""
Phase Management for Braille Writing Tutor
Handles the 6 tutoring phases and their specific logic
"""

import time
import threading
from typing import Dict, List, Optional
from gtts_config import get_braille_tts


class TutoringPhases:
    """Enumeration of tutoring phases"""
    OFF = 0
    EMBOSSING = 1
    CHARACTER_ID = 2
    MORPHOLOGY = 3
    SENTENCE = 4
    GAMIFICATION = 5
    FREEHAND = 6


class PhaseManager:
    """Manages tutoring phases and their specific behaviors"""
    
    def __init__(self):
        self.current_phase = TutoringPhases.OFF
        self._arduino = None  # Lazy loaded to avoid circular imports
        self._tts = None      # Lazy loaded
        
        # Phase-specific state
        self.current_input = ""
        self.current_cell = 0
        self.current_pattern = 0
        self.waiting_for_input = False
        self.lesson_progress = {}
        
        # Pattern storage for each phase
        self.stored_patterns = []
        self.current_word = ""
        self.current_sentence = ""
        
        # Game state for gamification phase
        self.game_score = 0
        self.game_attempts = 0
        self.current_animal = None
        
        # Register Arduino callbacks
        self._setup_arduino_callbacks()
    
    def _get_arduino(self):
        """Lazy load Arduino controller to avoid circular imports"""
        if self._arduino is None:
            from arduino_controller import get_arduino_controller
            self._arduino = get_arduino_controller()
        return self._arduino
    
    def _get_tts(self):
        """Lazy load TTS manager"""
        if self._tts is None:
            self._tts = get_braille_tts()
        return self._tts
    
    def _setup_arduino_callbacks(self):
        """Setup callbacks for Arduino messages"""
        try:
            arduino = self._get_arduino()
            arduino.register_callback('BUTTON_PRESS', self._handle_slate_button_press)
            arduino.register_callback('BUTTON_RELEASE', self._handle_slate_button_release)
            arduino.register_callback('DOT_PRESSED', self._handle_dot_press)
        except Exception as e:
            print(f"Error setting up Arduino callbacks: {e}")
    
    def get_current_phase(self) -> int:
        """Get the current phase"""
        return self.current_phase
    
    def set_phase(self, phase: int):
        """Set the current tutoring phase"""
        if phase == self.current_phase:
            return
            
        print(f"Switching from phase {self.current_phase} to phase {phase}")
        
        # Exit current phase
        self._exit_phase(self.current_phase)
        
        # Set new phase
        self.current_phase = phase
        
        # Initialize new phase
        self._enter_phase(phase)
        
        # Update Arduino
        try:
            arduino = self._get_arduino()
            arduino.set_phase(phase)
        except Exception as e:
            print(f"Error updating Arduino phase: {e}")
    
    def _exit_phase(self, phase: int):
        """Clean up when exiting a phase"""
        if phase == TutoringPhases.OFF:
            pass
        elif phase == TutoringPhases.EMBOSSING:
            try:
                arduino = self._get_arduino()
                arduino.clear_display()
            except:
                pass
        elif phase == TutoringPhases.CHARACTER_ID:
            self.stored_patterns.clear()
        elif phase == TutoringPhases.MORPHOLOGY:
            self.current_word = ""
        elif phase == TutoringPhases.SENTENCE:
            self.current_sentence = ""
        elif phase == TutoringPhases.GAMIFICATION:
            self._end_game()
        elif phase == TutoringPhases.FREEHAND:
            try:
                arduino = self._get_arduino()
                arduino.clear_display()
            except:
                pass
    
    def _enter_phase(self, phase: int):
        """Initialize when entering a phase"""
        self.waiting_for_input = False
        tts = self._get_tts()
        
        if phase == TutoringPhases.OFF:
            tts.speak("Sistema nakasara na. Salamat sa paggamit ng Braille Writing Tutor.")
            try:
                arduino = self._get_arduino()
                arduino.disable_display()
            except:
                pass
            
        elif phase == TutoringPhases.EMBOSSING:
            tts.speak("Maligayang pagdating sa Phase 1: Pag-aaral ng basic Braille dots")
            time.sleep(1)
            tts.speak("Mag-practice tayo ng mga tuldok. Pindutin ang stylus sa writing slate.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.display_text("DOTS")
            except:
                pass
            self.waiting_for_input = True
            
        elif phase == TutoringPhases.CHARACTER_ID:
            tts.speak("Maligayang pagdating sa Phase 2: Pag-aaral ng mga titik at numero")
            time.sleep(1)
            tts.speak("Matutuhan natin ang mga letra, numero, at punctuation marks.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.display_text("ABC")
            except:
                pass
            self.stored_patterns.clear()
            
        elif phase == TutoringPhases.MORPHOLOGY:
            tts.speak("Maligayang pagdating sa Phase 3: Pag-aaral ng mga salita")
            time.sleep(1)
            tts.speak("Matutuhan natin kung paano bumuo ng mga salita gamit ang Braille.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.clear_display()
            except:
                pass
            self.current_word = ""
            
        elif phase == TutoringPhases.SENTENCE:
            tts.speak("Maligayang pagdating sa Phase 4: Pag-aaral ng mga pangungusap")
            time.sleep(1)
            tts.speak("Matutuhan natin kung paano sumulat ng buong pangungusap.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.clear_display()
            except:
                pass
            self.current_sentence = ""
            
        elif phase == TutoringPhases.GAMIFICATION:
            tts.speak("Maligayang pagdating sa Phase 5: Larong pang-edukasyon")
            time.sleep(1)
            tts.speak("Maglaro tayo! Pakinggan ang tunog ng hayop at isulat ang pangalan.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.display_text("GAME")
            except:
                pass
            self._start_game()
            
        elif phase == TutoringPhases.FREEHAND:
            tts.speak("Maligayang pagdating sa Phase 6: Libreng pagsusulat")
            time.sleep(1)
            tts.speak("Sumulat ng kahit ano. Babasahin ko ang inyong sinulat.")
            try:
                arduino = self._get_arduino()
                arduino.enable_display()
                arduino.clear_display()
            except:
                pass
    
    def _handle_slate_button_press(self, row: int, col: int, cell: int, dot: int):
        """Handle button press from writing slate"""
        if not self.waiting_for_input:
            return
            
        if self.current_phase == TutoringPhases.EMBOSSING:
            self._handle_embossing_input(cell, dot)
        elif self.current_phase == TutoringPhases.CHARACTER_ID:
            self._handle_character_input(cell, dot)
        elif self.current_phase == TutoringPhases.MORPHOLOGY:
            self._handle_word_input(cell, dot)
        elif self.current_phase == TutoringPhases.SENTENCE:
            self._handle_sentence_input(cell, dot)
        elif self.current_phase == TutoringPhases.GAMIFICATION:
            self._handle_game_input(cell, dot)
        elif self.current_phase == TutoringPhases.FREEHAND:
            self._handle_freehand_input(cell, dot)
    
    def _handle_slate_button_release(self, row: int, col: int, cell: int, dot: int):
        """Handle button release from writing slate"""
        # Most phases don't need release handling
        pass
    
    def _handle_dot_press(self, cell: int, dot: int):
        """Handle dot press detection (from Arduino)"""
        if self.current_phase == TutoringPhases.EMBOSSING:
            tts = self._get_tts()
            tts.speak(f"Tuldok numero {dot} sa cell {cell + 1}")
    
    # Phase-specific input handlers
    def _handle_embossing_input(self, cell: int, dot: int):
        """Handle input in embossing phase"""
        if dot > 0:  # Valid dot (1-6)
            tts = self._get_tts()
            tts.speak(f"Napindot ninyo ang tuldok numero {dot}")
            # Show the dot on display
            pattern = 1 << (dot - 1)
            try:
                arduino = self._get_arduino()
                arduino.send_command(f"SET_CELL:{cell},{pattern}")
            except:
                pass
    
    def _handle_character_input(self, cell: int, dot: int):
        """Handle input in character identification phase"""
        if dot > 0:
            print(f"Character phase: Cell {cell}, Dot {dot}")
            # Build pattern for this cell
            # This would integrate with actual pattern recognition
    
    def _handle_word_input(self, cell: int, dot: int):
        """Handle input in morphology (word) phase"""
        if dot > 0:
            print(f"Word phase: Cell {cell}, Dot {dot}")
            # Build words across multiple cells
    
    def _handle_sentence_input(self, cell: int, dot: int):
        """Handle input in sentence phase"""
        if dot > 0:
            print(f"Sentence phase: Cell {cell}, Dot {dot}")
            # Build sentences with proper spacing
    
    def _handle_game_input(self, cell: int, dot: int):
        """Handle input in gamification phase"""
        if dot > 0:
            print(f"Game phase: Cell {cell}, Dot {dot}")
            # Handle game-specific input
    
    def _handle_freehand_input(self, cell: int, dot: int):
        """Handle input in freehand phase"""
        if dot > 0:
            print(f"Freehand phase: Cell {cell}, Dot {dot}")
            # Just echo whatever they write
    
    # Button action handlers (called from button_config.py)
    def handle_register_button(self):
        """Handle register button press"""
        tts = self._get_tts()
        
        if self.current_phase == TutoringPhases.OFF:
            tts.speak("Buksan muna ang sistema gamit ang knob.")
            return
            
        if self.current_phase == TutoringPhases.EMBOSSING:
            tts.speak("Na-register ang pattern. Tama ito.")
            tts.registered()
            
        elif self.current_phase == TutoringPhases.CHARACTER_ID:
            tts.speak("Na-register ang titik.")
            tts.registered()
            
        elif self.current_phase == TutoringPhases.MORPHOLOGY:
            tts.speak("Na-register ang salita.")
            tts.registered()
            
        elif self.current_phase == TutoringPhases.SENTENCE:
            tts.speak("Na-register ang pangungusap.")
            tts.registered()
            
        elif self.current_phase == TutoringPhases.GAMIFICATION:
            self.tts.speak("Na-register ang sagot.")
            # Check game answer
            
        elif self.current_phase == TutoringPhases.FREEHAND:
            self.tts.speak("Na-register ang teksto.")
            # Just acknowledge the input
    
    def handle_erase_button(self):
        """Handle erase button press"""
        if self.current_phase == TutoringPhases.OFF:
            return
            
        self.tts.speak("Na-erase ang input.")
        self.arduino.clear_display()
        
        # Clear phase-specific data
        if self.current_phase == TutoringPhases.CHARACTER_ID:
            self.stored_patterns.clear()
        elif self.current_phase == TutoringPhases.MORPHOLOGY:
            self.current_word = ""
        elif self.current_phase == TutoringPhases.SENTENCE:
            self.current_sentence = ""
    
    def handle_read_button(self):
        """Handle read button press"""
        if self.current_phase == TutoringPhases.OFF:
            return
            
        if self.current_phase == TutoringPhases.EMBOSSING:
            self.tts.speak("Ang kasalukuyang pattern ay para sa pag-practice ng mga tuldok.")
            
        elif self.current_phase == TutoringPhases.CHARACTER_ID:
            if self.stored_patterns:
                self.tts.speak("Babasahin ko ang mga naka-store na titik.")
                # Read back stored characters
            else:
                self.tts.speak("Walang naka-store na titik.")
                
        elif self.current_phase == TutoringPhases.MORPHOLOGY:
            if self.current_word:
                self.tts.speak(f"Ang kasalukuyang salita ay: {self.current_word}")
            else:
                self.tts.speak("Walang naka-type na salita.")
                
        elif self.current_phase == TutoringPhases.SENTENCE:
            if self.current_sentence:
                self.tts.speak(f"Ang kasalukuyang pangungusap ay: {self.current_sentence}")
            else:
                self.tts.speak("Walang naka-type na pangungusap.")
                
        elif self.current_phase == TutoringPhases.GAMIFICATION:
            self.tts.speak(f"Ang inyong score ay {self.game_score}.")
            
        elif self.current_phase == TutoringPhases.FREEHAND:
            self.tts.speak("Babasahin ko ang lahat ng naisulat ninyo.")
    
    def handle_display_button(self):
        """Handle display button press"""
        if self.current_phase == TutoringPhases.OFF:
            return
            
        self.tts.speak("Ipapakita sa mechanical display.")
        # The Arduino will handle the actual display
    
    # Game-specific methods
    def _start_game(self):
        """Start the gamification phase"""
        self.game_score = 0
        self.game_attempts = 0
        self.tts.speak("Simulan natin ang laro!")
        # Implementation for animal sounds game
    
    def _end_game(self):
        """End the gamification phase"""
        if self.game_score > 0:
            self.tts.speak(f"Tapos na ang laro! Ang inyong final score ay {self.game_score}.")
        self.game_score = 0
        self.game_attempts = 0
    
    def get_current_phase(self) -> int:
        """Get current phase number"""
        return self.current_phase
    
    def is_waiting_for_input(self) -> bool:
        """Check if system is waiting for user input"""
        return self.waiting_for_input


# Singleton management
_phase_manager_instance = None
_phase_manager_lock = threading.Lock()

def get_phase_manager() -> PhaseManager:
    """Get the singleton phase manager instance"""
    global _phase_manager_instance
    with _phase_manager_lock:
        if _phase_manager_instance is None:
            _phase_manager_instance = PhaseManager()
        return _phase_manager_instance

def cleanup_phase_manager():
    """Clean up the phase manager singleton"""
    global _phase_manager_instance
    with _phase_manager_lock:
        if _phase_manager_instance is not None:
            _phase_manager_instance.set_phase(TutoringPhases.OFF)
            _phase_manager_instance = None