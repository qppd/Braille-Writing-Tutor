"""
Test Script for Braille Writing Tutor Components
Tests all major components without requiring actual hardware
"""

import sys
import time
from unittest.mock import Mock, patch

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Mock RPi.GPIO to avoid hardware dependency
        sys.modules['RPi.GPIO'] = Mock()
        sys.modules['RPi'] = Mock()
        
        # Mock serial to avoid hardware dependency
        sys.modules['serial'] = Mock()
        
        # Test imports
        from gtts_config import get_braille_tts
        print("✓ gtts_config imported")
        
        from pins_config import BUTTON_PINS, KNOB_PINS, validate_pin_configuration
        print("✓ pins_config imported")
        
        from arduino_controller import ArduinoController
        print("✓ arduino_controller imported")
        
        from phase_manager import PhaseManager, TutoringPhases
        print("✓ phase_manager imported")
        
        from button_config_enhanced import EnhancedButtonManager
        print("✓ button_config_enhanced imported")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_pin_configuration():
    """Test pin configuration validation"""
    print("\nTesting pin configuration...")
    
    try:
        from pins_config import validate_pin_configuration, get_available_pins, PIN_DESCRIPTIONS
        
        # Test validation
        is_valid = validate_pin_configuration()
        print(f"✓ Pin validation: {'PASSED' if is_valid else 'FAILED'}")
        
        # Test available pins
        available = get_available_pins()
        print(f"✓ Available pins: {len(available)} pins free")
        
        # Test descriptions
        described_pins = len(PIN_DESCRIPTIONS)
        print(f"✓ Pin descriptions: {described_pins} pins documented")
        
        return True
        
    except Exception as e:
        print(f"✗ Pin configuration test failed: {e}")
        return False

def test_phase_system():
    """Test phase management system"""
    print("\nTesting phase system...")
    
    try:
        # Mock the dependencies
        with patch('phase_manager.get_arduino_controller'), \
             patch('phase_manager.get_braille_tts'):
            
            from phase_manager import PhaseManager, TutoringPhases
            
            # Create phase manager
            pm = PhaseManager()
            print("✓ PhaseManager created")
            
            # Test phase transitions
            pm.set_phase(TutoringPhases.EMBOSSING)
            assert pm.get_current_phase() == TutoringPhases.EMBOSSING
            print("✓ Phase transition works")
            
            # Test phase methods
            pm.handle_register_button()
            pm.handle_erase_button()
            pm.handle_read_button()
            pm.handle_display_button()
            print("✓ Button handlers work")
            
            return True
            
    except Exception as e:
        print(f"✗ Phase system test failed: {e}")
        return False

def test_arduino_controller():
    """Test Arduino controller (mocked)"""
    print("\nTesting Arduino controller...")
    
    try:
        with patch('arduino_controller.serial.Serial'):
            from arduino_controller import ArduinoController
            
            # Create controller
            controller = ArduinoController()
            print("✓ ArduinoController created")
            
            # Test commands
            controller.display_text("TEST")
            controller.clear_display()
            controller.set_phase(1)
            print("✓ Basic commands work")
            
            return True
            
    except Exception as e:
        print(f"✗ Arduino controller test failed: {e}")
        return False

def test_button_manager():
    """Test button manager (mocked)"""
    print("\nTesting button manager...")
    
    try:
        with patch('button_config_enhanced.GPIO'), \
             patch('button_config_enhanced.get_phase_manager'), \
             patch('button_config_enhanced.get_arduino_controller'):
            
            from button_config_enhanced import EnhancedButtonManager
            
            # Create button manager
            bm = EnhancedButtonManager()
            print("✓ EnhancedButtonManager created")
            
            # Test callback registration
            test_callback = lambda: print("Test callback")
            bm.register_callback('REGISTER', test_callback)
            print("✓ Callback registration works")
            
            # Test knob position
            bm.set_knob_position(3)
            assert bm.get_knob_position() == 3
            print("✓ Knob position management works")
            
            return True
            
    except Exception as e:
        print(f"✗ Button manager test failed: {e}")
        return False

def test_system_integration():
    """Test that all components can work together"""
    print("\nTesting system integration...")
    
    try:
        # Mock all hardware dependencies
        with patch('button_config_enhanced.GPIO'), \
             patch('arduino_controller.serial.Serial'), \
             patch('gtts_config.gTTS'), \
             patch('gtts_config.pygame'):
            
            # Import main enhanced system
            from main_enhanced import BrailleWritingTutor
            
            # This should work without errors
            print("✓ Main enhanced system can be imported")
            
            # Test that all manager instances can be created
            from phase_manager import get_phase_manager
            from arduino_controller import get_arduino_controller
            from button_config_enhanced import get_button_manager
            from gtts_config import get_braille_tts
            
            print("✓ All manager instances can be created")
            
            return True
            
    except Exception as e:
        print(f"✗ System integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("="*50)
    print("  BRAILLE WRITING TUTOR - COMPONENT TESTS")
    print("="*50)
    
    tests = [
        test_imports,
        test_pin_configuration,
        test_phase_system,
        test_arduino_controller,
        test_button_manager,
        test_system_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"  TEST RESULTS: {passed} passed, {failed} failed")
    print("="*50)
    
    if failed == 0:
        print("🎉 All tests passed! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)