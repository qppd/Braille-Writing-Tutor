#!/usr/bin/env python3
"""
Simple test script for gTTS integration
This script demonstrates the text-to-speech functionality without requiring GPIO
"""

import sys
import time
from gtts_config import get_tts_manager, get_braille_tts

def test_basic_tts():
    """Test basic TTS functionality"""
    print("Testing basic TTS functionality...")
    
    tts_manager = get_tts_manager()
    
    # Test basic speech
    print("Speaking: Hello World")
    tts_manager.speak("Hello World", blocking=True)
    
    time.sleep(1)
    
    # Test non-blocking speech
    print("Speaking (non-blocking): This is a test")
    tts_manager.speak("This is a test", blocking=False)
    
    time.sleep(3)  # Wait for speech to complete
    
def test_braille_tts():
    """Test Braille-specific TTS messages"""
    print("\nTesting Braille-specific TTS messages...")
    
    braille_tts = get_braille_tts()
    
    # Test welcome message
    print("Playing welcome message...")
    braille_tts.welcome()
    time.sleep(3)
    
    # Test button feedback
    print("Testing button feedback...")
    braille_tts.button_registered()
    time.sleep(2)
    
    braille_tts.pattern_erased()
    time.sleep(2)
    
    braille_tts.reading_pattern("Letter A")
    time.sleep(3)
    
    braille_tts.displaying_pattern()
    time.sleep(2)
    
def test_error_handling():
    """Test error handling and fallback"""
    print("\nTesting error handling...")
    
    braille_tts = get_braille_tts()
    
    # Test empty text
    braille_tts.tts.speak("")
    
    # Test error message
    braille_tts.error_message("Test error message")
    time.sleep(3)

def main():
    """Main test function"""
    print("gTTS Integration Test for Braille Writing Tutor")
    print("=" * 50)
    
    try:
        test_basic_tts()
        test_braille_tts()
        test_error_handling()
        
        print("\nPlaying shutdown message...")
        braille_tts = get_braille_tts()
        braille_tts.shutdown_message()
        time.sleep(3)
        
        print("\nAll tests completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure to install required packages:")
        print("pip3 install gtts pygame")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        
    finally:
        # Cleanup
        from gtts_config import cleanup_tts
        cleanup_tts()

if __name__ == '__main__':
    main()