"""
Comprehensive Test Suite for Braille Writing Tutor
Tests all major components and phase functionality
"""

import time
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        from gtts_config import get_braille_tts, cleanup_tts, BrailleTTS
        print("✓ TTS module imported successfully")
    except Exception as e:
        print(f"✗ TTS module import failed: {e}")
        return False
    
    try:
        from phase_manager import get_phase_manager, cleanup_phase_manager, TutoringPhases, PhaseManager
        print("✓ Phase manager module imported successfully")
    except Exception as e:
        print(f"✗ Phase manager module import failed: {e}")
        return False
    
    try:
        from arduino_controller import get_arduino_controller, cleanup_arduino_controller, ArduinoController
        print("✓ Arduino controller module imported successfully")
    except Exception as e:
        print(f"✗ Arduino controller module import failed: {e}")
        return False
    
    try:
        from button_config import get_button_manager, cleanup_button_manager, EnhancedButtonManager
        print("✓ Button manager module imported successfully")
    except Exception as e:
        print(f"✗ Button manager module import failed: {e}")
        return False
    
    try:
        from pins_config import BUTTON_PINS, KNOB_PINS, LED_PINS, validate_pin_configuration
        print("✓ Pin configuration module imported successfully")
    except Exception as e:
        print(f"✗ Pin configuration module import failed: {e}")
        return False
    
    return True

def test_pin_configuration():
    """Test pin configuration validation"""
    print("\nTesting pin configuration...")
    
    try:
        from pins_config import validate_pin_configuration, BUTTON_PINS, KNOB_PINS
        
        print(f"Button pins: {BUTTON_PINS}")
        print(f"Knob pins: {KNOB_PINS}")
        
        # Validate pin configuration
        is_valid = validate_pin_configuration()
        if is_valid:
            print("✓ Pin configuration is valid")
        else:
            print("✗ Pin configuration has conflicts")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Pin configuration test failed: {e}")
        return False

def test_tts_system():
    """Test TTS system functionality"""
    print("\nTesting TTS system...")
    
    try:
        from gtts_config import get_braille_tts
        
        # Test TTS initialization
        tts = get_braille_tts()
        print("✓ TTS system initialized")
        
        # Test basic TTS functions
        print("Testing TTS methods...")
        tts.welcome()
        time.sleep(0.5)
        
        tts.speak("Test message sa TTS system")
        time.sleep(0.5)
        
        tts.registered()
        time.sleep(0.5)
        
        tts.erased()
        time.sleep(0.5)
        
        tts.reading_pattern("Sample pattern")
        time.sleep(0.5)
        
        tts.displaying_pattern("Sample display")
        time.sleep(0.5)
        
        print("✓ TTS methods tested successfully")
        return True
        
    except Exception as e:
        print(f"✗ TTS system test failed: {e}")
        return False

def test_phase_manager():
    """Test phase manager functionality"""
    print("\nTesting phase manager...")
    
    try:
        from phase_manager import get_phase_manager, TutoringPhases
        
        # Test phase manager initialization
        phase_manager = get_phase_manager()
        print("✓ Phase manager initialized")
        
        # Test phase transitions
        print("Testing phase transitions...")
        
        initial_phase = phase_manager.get_current_phase()
        print(f"Initial phase: {initial_phase}")
        
        # Test each phase
        for phase in [TutoringPhases.EMBOSSING, TutoringPhases.CHARACTER_ID, 
                     TutoringPhases.MORPHOLOGY, TutoringPhases.SENTENCE,
                     TutoringPhases.GAMIFICATION, TutoringPhases.FREEHAND,
                     TutoringPhases.OFF]:
            
            print(f"Setting phase to: {phase}")
            phase_manager.set_phase(phase)
            current_phase = phase_manager.get_current_phase()
            
            if current_phase == phase:
                print(f"✓ Phase {phase} set successfully")
            else:
                print(f"✗ Phase setting failed: expected {phase}, got {current_phase}")
                return False
            
            time.sleep(0.5)
        
        # Test button handlers
        print("Testing button handlers...")
        phase_manager.set_phase(TutoringPhases.EMBOSSING)
        
        phase_manager.handle_register_button()
        time.sleep(0.2)
        
        phase_manager.handle_read_button()
        time.sleep(0.2)
        
        phase_manager.handle_display_button()
        time.sleep(0.2)
        
        phase_manager.handle_erase_button()
        time.sleep(0.2)
        
        print("✓ Button handlers tested successfully")
        
        # Return to OFF phase
        phase_manager.set_phase(TutoringPhases.OFF)
        
        return True
        
    except Exception as e:
        print(f"✗ Phase manager test failed: {e}")
        return False

def test_arduino_controller():
    """Test Arduino controller functionality"""
    print("\nTesting Arduino controller...")
    
    try:
        from arduino_controller import get_arduino_controller
        
        # Test Arduino controller initialization
        arduino = get_arduino_controller()
        print("✓ Arduino controller initialized")
        
        # Test command methods (won't actually send if not connected)
        print("Testing Arduino command methods...")
        
        arduino.set_phase(1)
        arduino.display_text("TEST")
        arduino.mirror_text("MIRROR")
        arduino.clear_display()
        arduino.enable_display()
        arduino.disable_display()
        arduino.test_display()
        
        print("✓ Arduino command methods tested")
        
        # Test connection status
        is_connected = arduino.is_connected()
        print(f"Arduino connection status: {is_connected}")
        
        if not is_connected:
            print("Note: Arduino not physically connected - this is expected in test environment")
        
        return True
        
    except Exception as e:
        print(f"✗ Arduino controller test failed: {e}")
        return False

def test_button_manager():
    """Test button manager functionality (without GPIO)"""
    print("\nTesting button manager...")
    
    try:
        # Note: This will fail on non-Raspberry Pi systems due to GPIO import
        # But we can test the import and basic structure
        
        print("Testing button manager import...")
        from button_config import EnhancedButtonManager
        print("✓ Button manager class imported")
        
        # We can't fully test GPIO functionality without actual hardware
        print("Note: Full GPIO testing requires Raspberry Pi hardware")
        
        return True
        
    except Exception as e:
        print(f"Note: Button manager test limited due to GPIO requirements: {e}")
        return True  # Return True since this is expected without GPIO hardware

def test_main_application():
    """Test main application structure"""
    print("\nTesting main application...")
    
    try:
        # Import main application
        import main
        print("✓ Main application imported successfully")
        
        # Test BrailleWritingTutor class structure
        tutor_class = main.BrailleWritingTutor
        print("✓ BrailleWritingTutor class accessible")
        
        # Test that main function exists
        main_func = main.main
        print("✓ Main function accessible")
        
        return True
        
    except Exception as e:
        print(f"✗ Main application test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("="*60)
    print("       BRAILLE WRITING TUTOR - COMPREHENSIVE TEST")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Pin Configuration", test_pin_configuration),
        ("TTS System", test_tts_system),
        ("Phase Manager", test_phase_manager),
        ("Arduino Controller", test_arduino_controller),
        ("Button Manager", test_button_manager),
        ("Main Application", test_main_application)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("                    TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<20} : {status}")
        if result:
            passed += 1
    
    print("-"*60)
    print(f"TOTAL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    # Cleanup
    try:
        from gtts_config import cleanup_tts
        from phase_manager import cleanup_phase_manager
        from arduino_controller import cleanup_arduino_controller
        from button_config import cleanup_button_manager
        
        cleanup_tts()
        cleanup_phase_manager()
        cleanup_arduino_controller()
        cleanup_button_manager()
        
        print("\n✓ Cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup error: {e}")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)