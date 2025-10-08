#ifndef BRAILLE_CONFIG_H
#define BRAILLE_CONFIG_H

#include <Arduino.h>

// Braille Display Configuration
// 10 Braille cells, each with 6 dots = 60 actuators total
// Each dot requires 2 outputs for bidirectional control (UP/DOWN)
// Total outputs needed: 60 dots × 2 directions = 120 outputs
// Using shift registers (74HC595) to control SMA coils/magnetic actuators

// Hardware Configuration
#define NUM_BRAILLE_CELLS 10
#define DOTS_PER_CELL 6
#define TOTAL_DOTS (NUM_BRAILLE_CELLS * DOTS_PER_CELL)
#define OUTPUTS_PER_DOT 2  // UP and DOWN control
#define TOTAL_OUTPUTS (TOTAL_DOTS * OUTPUTS_PER_DOT)  // 120 outputs

// Shift Register Pins
#define SR_DATA_PIN 2    // SER (Serial Data Input)
#define SR_CLOCK_PIN 3   // SRCLK (Shift Register Clock)
#define SR_LATCH_PIN 4   // RCLK (Register Clock / Latch)
#define SR_ENABLE_PIN 5  // OE (Output Enable) - Active LOW

// Number of shift registers needed (8 outputs per 74HC595)
#define NUM_SHIFT_REGISTERS ((TOTAL_OUTPUTS + 7) / 8)  // 15 registers for 120 outputs

// Dot control directions
#define DOT_DIRECTION_UP 0
#define DOT_DIRECTION_DOWN 1

// Actuator control timing
#define ACTUATOR_PULSE_TIME 100  // milliseconds to hold actuator active
#define ACTUATOR_SETTLE_TIME 50  // milliseconds between actuations

// Braille dot patterns for letters (standard 6-dot Braille)
// Bit positions: 0=dot1, 1=dot2, 2=dot3, 3=dot4, 4=dot5, 5=dot6
extern const uint8_t BRAILLE_ALPHABET[26];
extern const uint8_t BRAILLE_NUMBERS[10];
extern const uint8_t BRAILLE_PUNCTUATION[16];

// Special Braille characters
#define BRAILLE_CAPITAL_SIGN 0x20  // dot 6
#define BRAILLE_NUMBER_SIGN 0x3C   // dots 3,4,5,6
#define BRAILLE_SPACE 0x00         // no dots

// Braille cell structure
struct BrailleCell {
  uint8_t pattern;        // 6-bit pattern (dots 1-6)
  uint8_t currentState;   // Current physical state of dots (UP/DOWN)
  bool isActive;          // whether this cell is currently displayed
  unsigned long updateTime; // last update timestamp for timing
  bool needsUpdate;       // flag to indicate if physical update is needed
};

// Dot state structure for timing control
struct DotState {
  bool targetState;       // desired state (UP/DOWN)
  bool currentState;      // current physical state
  unsigned long actionTime; // when to perform the action
  bool actionPending;     // whether an action is scheduled
};

// Braille Display Class
class BrailleDisplay {
private:
  BrailleCell cells[NUM_BRAILLE_CELLS];
  DotState dotStates[TOTAL_DOTS];
  uint8_t shiftRegisterData[NUM_SHIFT_REGISTERS];
  bool displayEnabled;
  unsigned long lastUpdateTime;
  
  void updateShiftRegisters();
  void clearShiftRegisters();
  void setShiftRegisterBit(uint8_t outputIndex, bool state);
  uint8_t charToBraille(char c);
  void setDotState(uint8_t dotIndex, bool state, bool immediate = false);
  void processPendingActions();
  uint8_t getDotOutputIndex(uint8_t dotIndex, uint8_t direction);
  
public:
  BrailleDisplay();
  
  // Initialization
  void begin();
  void enable();
  void disable();
  
  // Display control
  void clearDisplay();
  void setCellPattern(uint8_t cellIndex, uint8_t pattern);
  void displayText(const char* text, uint8_t startCell = 0);
  void displayChar(char c, uint8_t cellIndex);
  
  // Bidirectional dot control
  void raiseDot(uint8_t cellIndex, uint8_t dotIndex);
  void lowerDot(uint8_t cellIndex, uint8_t dotIndex);
  void raiseDotImmediate(uint8_t cellIndex, uint8_t dotIndex);
  void lowerDotImmediate(uint8_t cellIndex, uint8_t dotIndex);
  
  // Mirror display for writing practice
  void displayMirroredPattern(uint8_t cellIndex, uint8_t pattern);
  void displayMirroredText(const char* text, uint8_t startCell = 0);
  
  // Status functions
  bool isEnabled() const { return displayEnabled; }
  uint8_t getCellPattern(uint8_t cellIndex) const;
  uint8_t getCurrentCellState(uint8_t cellIndex) const;
  void refresh(); // Update physical display
  void update();  // Process timing and pending actions
  
  // Test functions
  void testAllDots();
  void testSequential();
  void testPattern(uint8_t pattern);
  void testBidirectional();
};

// Global Braille Display instance
extern BrailleDisplay brailleDisplay;

// Utility functions
uint8_t mirrorBraillePattern(uint8_t pattern);
bool isValidBrailleCell(uint8_t cellIndex);
String patternToString(uint8_t pattern);

#endif // BRAILLE_CONFIG_H