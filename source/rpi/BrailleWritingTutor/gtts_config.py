"""
Google Text-to-Speech (gTTS) Configuration for Braille Writing Tutor
Handles text-to-speech functionality for audio feedback
"""

import os
import tempfile
import pygame
from gtts import gTTS
from io import BytesIO
import threading
import time


class TTSManager:
    """Manages text-to-speech functionality using Google TTS"""
    
    def __init__(self, language='en', slow=False):
        """
        Initialize TTS Manager
        
        Args:
            language (str): Language code (e.g., 'en', 'es', 'fr')
            slow (bool): Whether to speak slowly
        """
        self.language = language
        self.slow = slow
        self.is_speaking = False
        
        # Initialize pygame mixer for audio playback
        try:
            pygame.mixer.init()
            self.audio_available = True
            print("Audio system initialized successfully")
        except pygame.error as e:
            print(f"Warning: Audio system not available: {e}")
            self.audio_available = False
    
    def speak(self, text, blocking=False):
        """
        Convert text to speech and play it
        
        Args:
            text (str): Text to speak
            blocking (bool): If True, wait for speech to complete
        """
        if not self.audio_available:
            print(f"TTS: {text}")  # Fallback to console output
            return
            
        if not text or not text.strip():
            return
            
        if self.is_speaking and not blocking:
            return  # Skip if already speaking and non-blocking
            
        if blocking:
            self._speak_sync(text)
        else:
            # Speak asynchronously
            thread = threading.Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text):
        """
        Synchronously convert text to speech and play it
        
        Args:
            text (str): Text to speak
        """
        try:
            self.is_speaking = True
            
            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_filename = tmp_file.name
                
            tts.save(tmp_filename)
            
            # Play the audio file
            pygame.mixer.music.load(tmp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"TTS Error: {e}")
            print(f"Fallback text: {text}")
            
        finally:
            self.is_speaking = False
            # Clean up temporary file
            try:
                if 'tmp_filename' in locals():
                    os.unlink(tmp_filename)
            except:
                pass
    
    def stop(self):
        """Stop current speech"""
        if self.audio_available:
            pygame.mixer.music.stop()
        self.is_speaking = False
    
    def set_language(self, language):
        """
        Set the TTS language
        
        Args:
            language (str): Language code
        """
        self.language = language
    
    def set_slow_speech(self, slow):
        """
        Enable/disable slow speech
        
        Args:
            slow (bool): Whether to speak slowly
        """
        self.slow = slow
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        if self.audio_available:
            pygame.mixer.quit()


# Braille-specific TTS messages
class BrailleTTS:
    """Predefined messages for Braille Writing Tutor"""
    
    def __init__(self, tts_manager):
        self.tts = tts_manager
    
    def welcome(self):
        """Welcome message"""
        self.tts.speak("Welcome to Braille Writing Tutor. Press any button to begin.")
    
    def button_registered(self):
        """Button registration confirmation"""
        self.tts.speak("Pattern registered successfully.")
    
    def pattern_erased(self):
        """Pattern erase confirmation"""
        self.tts.speak("Pattern erased.")
    
    def reading_pattern(self, pattern_text=""):
        """Reading pattern announcement"""
        if pattern_text:
            self.tts.speak(f"Reading pattern: {pattern_text}")
        else:
            self.tts.speak("No pattern to read.")
    
    def displaying_pattern(self):
        """Display pattern announcement"""
        self.tts.speak("Displaying current pattern.")
    
    def error_message(self, error=""):
        """Error message"""
        message = f"Error: {error}" if error else "An error occurred."
        self.tts.speak(message)
    
    def shutdown_message(self):
        """Shutdown message"""
        self.tts.speak("Braille Writing Tutor shutting down. Goodbye!")


# Global TTS instance (singleton pattern)
_tts_manager = None
_braille_tts = None


def get_tts_manager():
    """Get global TTS manager instance"""
    global _tts_manager
    if _tts_manager is None:
        _tts_manager = TTSManager()
    return _tts_manager


def get_braille_tts():
    """Get global Braille TTS instance"""
    global _braille_tts
    if _braille_tts is None:
        _braille_tts = BrailleTTS(get_tts_manager())
    return _braille_tts


def cleanup_tts():
    """Cleanup TTS resources"""
    global _tts_manager, _braille_tts
    if _tts_manager:
        _tts_manager.cleanup()
        _tts_manager = None
        _braille_tts = None