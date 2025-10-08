/*
 * Braille Writing Tutor - Main Arduino Controller
 * 
 * This Arduino handles:
 * - 10-cell Braille display with SMA coils/magnetic actuators
 * - Serial communication with Raspberry Pi
 * - Communication with Writing Slate Arduino Mega
 * - Phase-based tutoring logic coordination
 * 
 * Hardware:
 * - Arduino Uno/Nano
 * - 74HC595 shift registers for actuator control
 * - Serial communication to RPi (USB) and Writing Slate (pins 0,1)
 * 
 * Communication Protocol:
 * From RPi: "PHASE:n", "DISPLAY:text", "MIRROR:text", "CLEAR", "TEST"
 * To RPi: "READY", "PHASE_SET:n", "DISPLAYED:text", "ERROR:msg"
 * From/To Slate: "BTN:row,col", "REL:row,col", "LED:row,col,state"
 */

#include "BRAILLE_CONFIG.h"
#include <SoftwareSerial.h>

// Configuration
#define BAUD_RATE 115200
#define SLATE_BAUD_RATE 115200

// Serial communication with Writing Slate (pins 7,8)
SoftwareSerial slateSerial(7, 8); // RX, TX

// System state
enum TutoringPhase {
  PHASE_OFF = 0,
  PHASE_EMBOSSING = 1,
  PHASE_CHARACTER_ID = 2,
  PHASE_MORPHOLOGY = 3,
  PHASE_SENTENCE = 4,
  PHASE_GAMIFICATION = 5,
  PHASE_FREEHAND = 6
};

struct SystemState {
  TutoringPhase currentPhase;
  bool isActive;
  String currentText;
  uint8_t currentCellIndex;
  uint8_t currentPattern;
  bool waitingForInput;
  unsigned long lastActivity;
} systemState;

// Input buffers
String rpiBuffer = "";
String slateBuffer = "";
bool rpiStringComplete = false;
bool slateStringComplete = false;

// Timing
unsigned long lastHeartbeat = 0;
const unsigned long HEARTBEAT_INTERVAL = 5000; // 5 seconds

void setup() {
  Serial.begin(BAUD_RATE);
  slateSerial.begin(SLATE_BAUD_RATE);
  
  // Initialize Braille display
  brailleDisplay.begin();
  
  // Initialize system state
  initializeSystem();
  
  // Send ready signal to RPi
  Serial.println(F("READY"));
  
  // Send test command to slate
  slateSerial.println(F("STATUS"));
  
  Serial.println(F("Braille Writing Tutor Controller Ready"));
  Serial.println(F("Commands: PHASE:n, DISPLAY:text, MIRROR:text, CLEAR, TEST"));
}

void loop() {
  // Process serial communications
  processRPiCommunication();
  processSlateCommunication();
  
  // Handle phase-specific logic
  handleCurrentPhase();
  
  // Update Braille display (process pending dot actions)
  brailleDisplay.update();
  
  // Send periodic heartbeat
  sendHeartbeat();
  
  delay(10); // Small delay to prevent overwhelming
}

void initializeSystem() {
  systemState.currentPhase = PHASE_OFF;
  systemState.isActive = false;
  systemState.currentText = "";
  systemState.currentCellIndex = 0;
  systemState.currentPattern = 0;
  systemState.waitingForInput = false;
  systemState.lastActivity = millis();
  
  brailleDisplay.clearDisplay();
  
  Serial.println(F("System initialized"));
}

void processRPiCommunication() {
  // Read from RPi
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    rpiBuffer += inChar;
    
    if (inChar == '\n') {
      rpiStringComplete = true;
    }
  }
  
  // Process complete command from RPi
  if (rpiStringComplete) {
    rpiBuffer.trim();
    processRPiCommand(rpiBuffer);
    rpiBuffer = "";
    rpiStringComplete = false;
  }
}

void processSlateCommunication() {
  // Read from Writing Slate
  while (slateSerial.available()) {
    char inChar = (char)slateSerial.read();
    slateBuffer += inChar;
    
    if (inChar == '\n') {
      slateStringComplete = true;
    }
  }
  
  // Process complete message from slate
  if (slateStringComplete) {
    slateBuffer.trim();
    processSlateMessage(slateBuffer);
    slateBuffer = "";
    slateStringComplete = false;
  }
}

void processRPiCommand(String command) {
  systemState.lastActivity = millis();
  
  if (command.startsWith("PHASE:")) {
    // Set tutoring phase
    int phase = command.substring(6).toInt();
    setTutoringPhase((TutoringPhase)phase);
    
  } else if (command.startsWith("DISPLAY:")) {
    // Display text normally
    String text = command.substring(8);
    displayText(text, false);
    
  } else if (command.startsWith("MIRROR:")) {
    // Display mirrored text for writing practice
    String text = command.substring(7);
    displayText(text, true);
    
  } else if (command.equals("CLEAR")) {
    // Clear display
    clearDisplay();
    
  } else if (command.equals("ENABLE")) {
    // Enable display
    brailleDisplay.enable();
    Serial.println(F("DISPLAY_ENABLED"));
    
  } else if (command.equals("DISABLE")) {
    // Disable display
    brailleDisplay.disable();
    Serial.println(F("DISPLAY_DISABLED"));
    
  } else if (command.equals("TEST")) {
    // Run test sequence
    runTestSequence();
    
  } else if (command.equals("STATUS")) {
    // Send status
    sendStatus();
    
  } else {
    // Unknown command
    Serial.print(F("ERROR:Unknown command: "));
    Serial.println(command);
  }
}

void processSlateMessage(String message) {
  if (message.startsWith("BTN:")) {
    // Button press from slate
    int commaIndex = message.indexOf(',');
    if (commaIndex > 0) {
      uint8_t row = message.substring(4, commaIndex).toInt();
      uint8_t col = message.substring(commaIndex + 1).toInt();
      handleButtonPress(row, col);
    }
    
  } else if (message.startsWith("REL:")) {
    // Button release from slate
    int commaIndex = message.indexOf(',');
    if (commaIndex > 0) {
      uint8_t row = message.substring(4, commaIndex).toInt();
      uint8_t col = message.substring(commaIndex + 1).toInt();
      handleButtonRelease(row, col);
    }
    
  } else {
    // Forward other messages to RPi for logging
    Serial.print(F("SLATE:"));
    Serial.println(message);
  }
}

void setTutoringPhase(TutoringPhase phase) {
  if (phase == systemState.currentPhase) {
    return; // No change needed
  }
  
  systemState.currentPhase = phase;
  systemState.isActive = (phase != PHASE_OFF);
  
  if (systemState.isActive) {
    brailleDisplay.enable();
  } else {
    brailleDisplay.disable();
    brailleDisplay.clearDisplay();
  }
  
  // Send confirmation to RPi
  Serial.print(F("PHASE_SET:"));
  Serial.println((int)phase);
  
  // Initialize phase-specific setup
  initializePhase(phase);
  
  Serial.print(F("Phase set to: "));
  Serial.println((int)phase);
}

void initializePhase(TutoringPhase phase) {
  systemState.currentCellIndex = 0;
  systemState.currentPattern = 0;
  systemState.waitingForInput = false;
  
  switch (phase) {
    case PHASE_OFF:
      brailleDisplay.clearDisplay();
      break;
      
    case PHASE_EMBOSSING:
      // Show welcome pattern
      brailleDisplay.displayText("DOTS", 0);
      systemState.waitingForInput = true;
      break;
      
    case PHASE_CHARACTER_ID:
      // Show alphabet starting position
      brailleDisplay.displayText("ABC", 0);
      break;
      
    case PHASE_MORPHOLOGY:
      // Clear for word practice
      brailleDisplay.clearDisplay();
      break;
      
    case PHASE_SENTENCE:
      // Clear for sentence practice
      brailleDisplay.clearDisplay();
      break;
      
    case PHASE_GAMIFICATION:
      // Show game ready state
      brailleDisplay.displayText("GAME", 0);
      break;
      
    case PHASE_FREEHAND:
      // Clear for free writing
      brailleDisplay.clearDisplay();
      break;
  }
}

void displayText(String text, bool mirrored) {
  systemState.currentText = text;
  
  if (mirrored) {
    brailleDisplay.displayMirroredText(text.c_str(), 0);
    Serial.print(F("MIRRORED:"));
  } else {
    brailleDisplay.displayText(text.c_str(), 0);
    Serial.print(F("DISPLAYED:"));
  }
  Serial.println(text);
}

void clearDisplay() {
  brailleDisplay.clearDisplay();
  systemState.currentText = "";
  systemState.currentCellIndex = 0;
  Serial.println(F("CLEARED"));
}

void handleButtonPress(uint8_t row, uint8_t col) {
  // Convert button position to Braille cell and dot
  uint8_t cellIndex, dotIndex;
  mapButtonToBraille(row, col, &cellIndex, &dotIndex);
  
  // Send position info to RPi for processing
  Serial.print(F("BUTTON_PRESS:"));
  Serial.print(row);
  Serial.print(F(","));
  Serial.print(col);
  Serial.print(F(","));
  Serial.print(cellIndex);
  Serial.print(F(","));
  Serial.println(dotIndex);
  
  // Phase-specific handling
  handlePhaseSpecificInput(cellIndex, dotIndex, true);
}

void handleButtonRelease(uint8_t row, uint8_t col) {
  uint8_t cellIndex, dotIndex;
  mapButtonToBraille(row, col, &cellIndex, &dotIndex);
  
  Serial.print(F("BUTTON_RELEASE:"));
  Serial.print(row);
  Serial.print(F(","));
  Serial.print(col);
  Serial.print(F(","));
  Serial.print(cellIndex);
  Serial.print(F(","));
  Serial.println(dotIndex);
  
  handlePhaseSpecificInput(cellIndex, dotIndex, false);
}

void handlePhaseSpecificInput(uint8_t cellIndex, uint8_t dotIndex, bool pressed) {
  switch (systemState.currentPhase) {
    case PHASE_EMBOSSING:
      if (pressed && dotIndex > 0) {
        // Show the pressed dot
        uint8_t pattern = 1 << (dotIndex - 1);
        brailleDisplay.setCellPattern(cellIndex, pattern);
        
        // Send dot position to RPi
        Serial.print(F("DOT_PRESSED:"));
        Serial.print(cellIndex);
        Serial.print(F(","));
        Serial.println(dotIndex);
      }
      break;
      
    case PHASE_CHARACTER_ID:
    case PHASE_MORPHOLOGY:
    case PHASE_SENTENCE:
    case PHASE_FREEHAND:
      // Let RPi handle the logic and send display commands
      break;
      
    case PHASE_GAMIFICATION:
      // Game-specific input handling
      if (pressed) {
        Serial.print(F("GAME_INPUT:"));
        Serial.print(cellIndex);
        Serial.print(F(","));
        Serial.println(dotIndex);
      }
      break;
  }
}

void mapButtonToBraille(uint8_t row, uint8_t col, uint8_t* cellIndex, uint8_t* dotIndex) {
  // Map 10x10 button matrix to Braille cells
  // Each cell occupies a 2x3 area, allowing for multiple cells
  
  *cellIndex = (row / 4) * 3 + (col / 3);
  if (*cellIndex >= NUM_BRAILLE_CELLS) {
    *cellIndex = NUM_BRAILLE_CELLS - 1;
  }
  
  // Map position within cell to dot number (1-6)
  uint8_t localRow = row % 4;
  uint8_t localCol = col % 3;
  
  if (localRow < 3 && localCol < 2) {
    *dotIndex = localRow * 2 + localCol + 1;
  } else {
    *dotIndex = 0; // Invalid dot position
  }
}

void handleCurrentPhase() {
  // Phase-specific periodic tasks
  switch (systemState.currentPhase) {
    case PHASE_OFF:
      // Do nothing when off
      break;
      
    case PHASE_EMBOSSING:
      // Could add automatic dot demonstrations
      break;
      
    case PHASE_CHARACTER_ID:
    case PHASE_MORPHOLOGY:
    case PHASE_SENTENCE:
    case PHASE_FREEHAND:
      // RPi handles the main logic
      break;
      
    case PHASE_GAMIFICATION:
      // Could add game timing logic
      break;
  }
}

void runTestSequence() {
  Serial.println(F("TEST_START"));
  
  // Test Braille display
  brailleDisplay.testSequential();
  
  // Test communication with slate
  slateSerial.println(F("TEST"));
  
  Serial.println(F("TEST_COMPLETE"));
}

void sendStatus() {
  Serial.println(F("STATUS_START"));
  Serial.print(F("PHASE:"));
  Serial.println((int)systemState.currentPhase);
  Serial.print(F("ACTIVE:"));
  Serial.println(systemState.isActive ? F("true") : F("false"));
  Serial.print(F("DISPLAY_ENABLED:"));
  Serial.println(brailleDisplay.isEnabled() ? F("true") : F("false"));
  Serial.print(F("CURRENT_TEXT:"));
  Serial.println(systemState.currentText);
  Serial.print(F("CELL_INDEX:"));
  Serial.println(systemState.currentCellIndex);
  Serial.print(F("UPTIME:"));
  Serial.println(millis());
  Serial.println(F("STATUS_END"));
}

void sendHeartbeat() {
  if (millis() - lastHeartbeat > HEARTBEAT_INTERVAL) {
    Serial.println(F("HEARTBEAT"));
    lastHeartbeat = millis();
  }
}
