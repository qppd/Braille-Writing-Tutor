# Braille Writing Tutor - Raspberry Pi Setup

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure your Raspberry Pi has GPIO access enabled.

## Hardware Setup

### Button Connections (using BCM pin numbering):
- **Register Button**: Connect to GPIO 18 (Pin 12)
- **Erase Button**: Connect to GPIO 19 (Pin 35)  
- **Read Button**: Connect to GPIO 20 (Pin 38)
- **Display Button**: Connect to GPIO 21 (Pin 40)

### Wiring:
- Connect one side of each button to the respective GPIO pin
- Connect the other side of each button to GND
- The code uses internal pull-up resistors, so no external resistors needed

## Text-to-Speech (TTS) Setup

The application now includes Google Text-to-Speech (gTTS) for audio feedback:

### TTS Dependencies
- **gTTS**: Google Text-to-Speech library
- **pygame**: Audio playback for TTS

### TTS Features
- Welcome message on startup
- Audio feedback for each button press
- Customizable language and speech speed
- Automatic cleanup and error handling
- Non-blocking audio playback

### Testing TTS
Test the TTS functionality without GPIO hardware:
```bash
python test_tts.py
```

## Usage

Run the main application:
```bash
python main.py
```

## Button Functions

- **Register Button**: Records/saves the current Braille pattern
- **Erase Button**: Clears the current input
- **Read Button**: Reads back stored Braille patterns
- **Display Button**: Shows/displays the current pattern

## Threading Implementation

The button system uses threading for responsive, non-blocking operation:

- **GPIO Interrupts**: Button presses trigger hardware interrupts
- **Threaded Callbacks**: Each button press spawns a separate thread
- **Debouncing**: Hardware-level debouncing prevents false triggers
- **Thread Safety**: Uses locks to prevent race conditions
- **Non-blocking**: Main application loop remains responsive

## File Structure

- `main.py`: Main application entry point
- `button_config.py`: Button handling and callback management
- `pins_config.py`: GPIO pin configuration
- `requirements.txt`: Python dependencies

## Customization

To modify button behavior, edit the callback functions in `button_config.py`:
- `on_register_button()`
- `on_erase_button()`
- `on_read_button()`
- `on_display_button()`

To change GPIO pins, modify the `BUTTON_PINS` dictionary in `pins_config.py`.