#include "BRAILLE_CONFIG.h"

// Braille alphabet patterns (A-Z)
// Bit positions: 0=dot1, 1=dot2, 2=dot3, 3=dot4, 4=dot5, 5=dot6
const uint8_t BRAILLE_ALPHABET[26] = {
  0x01, // A (dot 1)
  0x03, // B (dots 1,2)
  0x09, // C (dots 1,4)
  0x19, // D (dots 1,4,5)
  0x11, // E (dots 1,5)
  0x0B, // F (dots 1,2,4)
  0x1B, // G (dots 1,2,4,5)
  0x13, // H (dots 1,2,5)
  0x0A, // I (dots 2,4)
  0x1A, // J (dots 2,4,5)
  0x05, // K (dots 1,3)
  0x07, // L (dots 1,2,3)
  0x0D, // M (dots 1,3,4)
  0x1D, // N (dots 1,3,4,5)
  0x15, // O (dots 1,3,5)
  0x0F, // P (dots 1,2,3,4)
  0x1F, // Q (dots 1,2,3,4,5)
  0x17, // R (dots 1,2,3,5)
  0x0E, // S (dots 2,3,4)
  0x1E, // T (dots 2,3,4,5)
  0x25, // U (dots 1,3,6)
  0x27, // V (dots 1,2,3,6)
  0x3A, // W (dots 2,4,5,6)
  0x2D, // X (dots 1,3,4,6)
  0x3D, // Y (dots 1,3,4,5,6)
  0x35  // Z (dots 1,3,5,6)
};

// Braille number patterns (0-9)
// Numbers use the same patterns as letters A-J with number prefix
const uint8_t BRAILLE_NUMBERS[10] = {
  0x1A, // 0 (same as J)
  0x01, // 1 (same as A)
  0x03, // 2 (same as B)
  0x09, // 3 (same as C)
  0x19, // 4 (same as D)
  0x11, // 5 (same as E)
  0x0B, // 6 (same as F)
  0x1B, // 7 (same as G)
  0x13, // 8 (same as H)
  0x0A  // 9 (same as I)
};

// Common punctuation patterns
const uint8_t BRAILLE_PUNCTUATION[16] = {
  0x00, // Space
  0x16, // ! (dots 2,3,5)
  0x04, // ' (dot 3)
  0x30, // - (dots 3,6)
  0x32, // . (dots 2,5,6)
  0x0C, // , (dot 2)
  0x26, // ? (dots 2,6)
  0x06, // ; (dots 2,3)
  0x12, // : (dots 2,5)
  0x23, // ( (dots 1,2,6)
  0x1C, // ) (dots 3,4,5)
  0x2C, // " opening (dots 2,3,6)
  0x18, // " closing (dots 3,4,5)
  0x2E, // / (dots 2,3,4,6)
  0x2A, // * (dots 2,4,6)
  0x24  // @ (dots 3,6)
};

// Global instance
BrailleDisplay brailleDisplay;

// Constructor
BrailleDisplay::BrailleDisplay() {
  displayEnabled = false;
  lastUpdateTime = 0;
  
  // Initialize cells
  for (int i = 0; i < NUM_BRAILLE_CELLS; i++) {
    cells[i].pattern = 0;
    cells[i].currentState = 0;
    cells[i].isActive = false;
    cells[i].updateTime = 0;
    cells[i].needsUpdate = false;
  }
  
  // Initialize dot states
  for (int i = 0; i < TOTAL_DOTS; i++) {
    dotStates[i].targetState = false;    // DOWN (retracted)
    dotStates[i].currentState = false;   // DOWN (retracted)
    dotStates[i].actionTime = 0;
    dotStates[i].actionPending = false;
  }
  
  // Clear shift register data
  clearShiftRegisters();
}

// Initialize the Braille display hardware
void BrailleDisplay::begin() {
  // Configure shift register pins
  pinMode(SR_DATA_PIN, OUTPUT);
  pinMode(SR_CLOCK_PIN, OUTPUT);
  pinMode(SR_LATCH_PIN, OUTPUT);
  pinMode(SR_ENABLE_PIN, OUTPUT);
  
  // Initialize pins to safe state
  digitalWrite(SR_DATA_PIN, LOW);
  digitalWrite(SR_CLOCK_PIN, LOW);
  digitalWrite(SR_LATCH_PIN, LOW);
  digitalWrite(SR_ENABLE_PIN, HIGH); // Disable output initially
  
  clearDisplay();
  Serial.println(F("Braille Display initialized"));
  Serial.print(F("Total cells: "));
  Serial.println(NUM_BRAILLE_CELLS);
  Serial.print(F("Total dots: "));
  Serial.println(TOTAL_DOTS);
  Serial.print(F("Total outputs: "));
  Serial.println(TOTAL_OUTPUTS);
  Serial.print(F("Shift registers: "));
  Serial.println(NUM_SHIFT_REGISTERS);
}

// Enable the display
void BrailleDisplay::enable() {
  displayEnabled = true;
  digitalWrite(SR_ENABLE_PIN, LOW); // Enable shift register outputs
  refresh();
  Serial.println(F("Braille Display enabled"));
}

// Disable the display
void BrailleDisplay::disable() {
  displayEnabled = false;
  digitalWrite(SR_ENABLE_PIN, HIGH); // Disable shift register outputs
  Serial.println(F("Braille Display disabled"));
}

// Clear all cells
void BrailleDisplay::clearDisplay() {
  for (int i = 0; i < NUM_BRAILLE_CELLS; i++) {
    cells[i].pattern = 0;
    cells[i].currentState = 0;
    cells[i].isActive = false;
    cells[i].updateTime = millis();
    cells[i].needsUpdate = true;
  }
  
  // Set all dots to DOWN (retracted) state
  for (int i = 0; i < TOTAL_DOTS; i++) {
    setDotState(i, false, false); // Schedule for lowering
  }
  
  clearShiftRegisters();
  if (displayEnabled) {
    refresh();
  }
}

// Clear shift register data array
void BrailleDisplay::clearShiftRegisters() {
  for (int i = 0; i < NUM_SHIFT_REGISTERS; i++) {
    shiftRegisterData[i] = 0;
  }
}

// Set pattern for a specific cell
void BrailleDisplay::setCellPattern(uint8_t cellIndex, uint8_t pattern) {
  if (!isValidBrailleCell(cellIndex)) {
    Serial.print(F("Invalid cell index: "));
    Serial.println(cellIndex);
    return;
  }
  
  cells[cellIndex].pattern = pattern & 0x3F; // Mask to 6 bits
  cells[cellIndex].isActive = (pattern != 0);
  cells[cellIndex].updateTime = millis();
  cells[cellIndex].needsUpdate = true;
  
  // Update individual dot states based on pattern
  for (uint8_t dot = 0; dot < DOTS_PER_CELL; dot++) {
    uint8_t absoluteDotIndex = cellIndex * DOTS_PER_CELL + dot;
    bool dotShouldBeUp = (pattern & (1 << dot)) != 0;
    setDotState(absoluteDotIndex, dotShouldBeUp, false);
  }
  
  // Update current state tracking
  cells[cellIndex].currentState = pattern;
  
  if (displayEnabled) {
    // Process immediately if display is enabled
    processPendingActions();
  }
}

// Display text starting from specified cell
void BrailleDisplay::displayText(const char* text, uint8_t startCell) {
  if (text == nullptr || startCell >= NUM_BRAILLE_CELLS) {
    return;
  }
  
  clearDisplay();
  
  uint8_t cellIndex = startCell;
  uint8_t textIndex = 0;
  bool numberMode = false;
  
  while (text[textIndex] != '\0' && cellIndex < NUM_BRAILLE_CELLS) {
    char c = text[textIndex];
    
    // Handle special characters
    if (c >= '0' && c <= '9') {
      if (!numberMode) {
        // Add number sign before first digit
        if (cellIndex < NUM_BRAILLE_CELLS) {
          setCellPattern(cellIndex++, BRAILLE_NUMBER_SIGN);
          numberMode = true;
        }
      }
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, BRAILLE_NUMBERS[c - '0']);
      }
    } else if (c >= 'A' && c <= 'Z') {
      numberMode = false;
      // Add capital sign before uppercase letter
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, BRAILLE_CAPITAL_SIGN);
      }
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, BRAILLE_ALPHABET[c - 'A']);
      }
    } else if (c >= 'a' && c <= 'z') {
      numberMode = false;
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, BRAILLE_ALPHABET[c - 'a']);
      }
    } else if (c == ' ') {
      numberMode = false;
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, BRAILLE_SPACE);
      }
    } else {
      numberMode = false;
      // Handle punctuation (simplified)
      uint8_t pattern = charToBraille(c);
      if (cellIndex < NUM_BRAILLE_CELLS) {
        setCellPattern(cellIndex++, pattern);
      }
    }
    
    textIndex++;
  }
  
  Serial.print(F("Displayed text: \""));
  Serial.print(text);
  Serial.print(F("\" in "));
  Serial.print(cellIndex - startCell);
  Serial.println(F(" cells"));
}

// Display single character
void BrailleDisplay::displayChar(char c, uint8_t cellIndex) {
  if (!isValidBrailleCell(cellIndex)) {
    return;
  }
  
  uint8_t pattern = charToBraille(c);
  setCellPattern(cellIndex, pattern);
}

// Display mirrored pattern (for writing practice)
void BrailleDisplay::displayMirroredPattern(uint8_t cellIndex, uint8_t pattern) {
  uint8_t mirroredPattern = mirrorBraillePattern(pattern);
  setCellPattern(cellIndex, mirroredPattern);
}

// Display mirrored text
void BrailleDisplay::displayMirroredText(const char* text, uint8_t startCell) {
  // First display normal text to get patterns
  displayText(text, startCell);
  
  // Then mirror each active cell
  for (uint8_t i = startCell; i < NUM_BRAILLE_CELLS; i++) {
    if (cells[i].isActive) {
      cells[i].pattern = mirrorBraillePattern(cells[i].pattern);
    }
  }
  
  updateShiftRegisters();
  if (displayEnabled) {
    refresh();
  }
  
  Serial.print(F("Displayed mirrored text: \""));
  Serial.print(text);
  Serial.println(F("\""));
}

// Get pattern for specific cell
uint8_t BrailleDisplay::getCellPattern(uint8_t cellIndex) const {
  if (!isValidBrailleCell(cellIndex)) {
    return 0;
  }
  return cells[cellIndex].pattern;
}

// Convert character to Braille pattern
uint8_t BrailleDisplay::charToBraille(char c) {
  if (c >= 'a' && c <= 'z') {
    return BRAILLE_ALPHABET[c - 'a'];
  } else if (c >= 'A' && c <= 'Z') {
    return BRAILLE_ALPHABET[c - 'A'];
  } else if (c >= '0' && c <= '9') {
    return BRAILLE_NUMBERS[c - '0'];
  } else {
    // Handle common punctuation
    switch (c) {
      case ' ': return BRAILLE_SPACE;
      case '!': return BRAILLE_PUNCTUATION[1];
      case '\'': return BRAILLE_PUNCTUATION[2];
      case '-': return BRAILLE_PUNCTUATION[3];
      case '.': return BRAILLE_PUNCTUATION[4];
      case ',': return BRAILLE_PUNCTUATION[5];
      case '?': return BRAILLE_PUNCTUATION[6];
      case ';': return BRAILLE_PUNCTUATION[7];
      case ':': return BRAILLE_PUNCTUATION[8];
      default: return 0;
    }
  }
}

// Update shift register data based on dot states
void BrailleDisplay::updateShiftRegisters() {
  clearShiftRegisters();
  
  for (uint8_t dotIndex = 0; dotIndex < TOTAL_DOTS; dotIndex++) {
    bool dotState = dotStates[dotIndex].currentState;
    
    // Each dot has two outputs: UP and DOWN
    uint8_t upOutputIndex = getDotOutputIndex(dotIndex, DOT_DIRECTION_UP);
    uint8_t downOutputIndex = getDotOutputIndex(dotIndex, DOT_DIRECTION_DOWN);
    
    // Set appropriate output based on desired state
    if (dotState) {
      // Dot should be UP (raised)
      setShiftRegisterBit(upOutputIndex, true);
      setShiftRegisterBit(downOutputIndex, false);
    } else {
      // Dot should be DOWN (retracted)
      setShiftRegisterBit(upOutputIndex, false);
      setShiftRegisterBit(downOutputIndex, true);
    }
  }
}

// Helper function to set specific bit in shift register array
void BrailleDisplay::setShiftRegisterBit(uint8_t outputIndex, bool state) {
  if (outputIndex >= TOTAL_OUTPUTS) return;
  
  uint8_t registerIndex = outputIndex / 8;
  uint8_t bitIndex = outputIndex % 8;
  
  if (registerIndex < NUM_SHIFT_REGISTERS) {
    if (state) {
      shiftRegisterData[registerIndex] |= (1 << bitIndex);
    } else {
      shiftRegisterData[registerIndex] &= ~(1 << bitIndex);
    }
  }
}

// Refresh physical display
void BrailleDisplay::refresh() {
  if (!displayEnabled) {
    return;
  }
  
  // Shift out data to registers (MSB first)
  digitalWrite(SR_LATCH_PIN, LOW);
  
  for (int i = NUM_SHIFT_REGISTERS - 1; i >= 0; i--) {
    shiftOut(SR_DATA_PIN, SR_CLOCK_PIN, MSBFIRST, shiftRegisterData[i]);
  }
  
  digitalWrite(SR_LATCH_PIN, HIGH);
  lastUpdateTime = millis();
}

// Test all dots sequentially
void BrailleDisplay::testAllDots() {
  Serial.println(F("Testing all dots..."));
  
  clearDisplay();
  enable();
  
  // Test each dot in each cell
  for (uint8_t cell = 0; cell < NUM_BRAILLE_CELLS; cell++) {
    for (uint8_t dot = 0; dot < DOTS_PER_CELL; dot++) {
      setCellPattern(cell, 1 << dot);
      delay(200);
    }
    setCellPattern(cell, 0);
  }
  
  Serial.println(F("Dot test complete"));
}

// Test sequential patterns
void BrailleDisplay::testSequential() {
  Serial.println(F("Testing sequential patterns..."));
  
  clearDisplay();
  enable();
  
  // Test common patterns
  uint8_t testPatterns[] = {0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F};
  
  for (uint8_t i = 0; i < 6; i++) {
    for (uint8_t cell = 0; cell < NUM_BRAILLE_CELLS; cell++) {
      setCellPattern(cell, testPatterns[i]);
      delay(100);
    }
    delay(500);
    clearDisplay();
  }
  
  Serial.println(F("Sequential test complete"));
}

// Test specific pattern
void BrailleDisplay::testPattern(uint8_t pattern) {
  Serial.print(F("Testing pattern: 0x"));
  Serial.print(pattern, HEX);
  Serial.print(F(" ("));
  Serial.print(patternToString(pattern));
  Serial.println(F(")"));
  
  clearDisplay();
  enable();
  
  for (uint8_t cell = 0; cell < NUM_BRAILLE_CELLS; cell++) {
    setCellPattern(cell, pattern);
  }
  
  delay(2000);
  clearDisplay();
}

// Test bidirectional control
void BrailleDisplay::testBidirectional() {
  Serial.println(F("Testing bidirectional control..."));
  
  clearDisplay();
  enable();
  
  // Test each dot individually - raise then lower
  for (uint8_t cell = 0; cell < NUM_BRAILLE_CELLS && cell < 3; cell++) { // Test first 3 cells
    for (uint8_t dot = 0; dot < DOTS_PER_CELL; dot++) {
      Serial.print(F("Testing Cell "));
      Serial.print(cell);
      Serial.print(F(", Dot "));
      Serial.println(dot + 1);
      
      // Raise dot
      raiseDotImmediate(cell, dot);
      delay(500);
      
      // Lower dot
      lowerDotImmediate(cell, dot);
      delay(500);
    }
  }
  
  Serial.println(F("Bidirectional test complete"));
}

// Set dot state with timing control
void BrailleDisplay::setDotState(uint8_t dotIndex, bool state, bool immediate) {
  if (dotIndex >= TOTAL_DOTS) return;
  
  dotStates[dotIndex].targetState = state;
  
  if (immediate) {
    dotStates[dotIndex].currentState = state;
    dotStates[dotIndex].actionTime = millis();
    dotStates[dotIndex].actionPending = false;
    updateShiftRegisters();
    refresh();
  } else {
    dotStates[dotIndex].actionTime = millis() + ACTUATOR_SETTLE_TIME;
    dotStates[dotIndex].actionPending = true;
  }
}

// Raise specific dot
void BrailleDisplay::raiseDot(uint8_t cellIndex, uint8_t dotIndex) {
  if (cellIndex >= NUM_BRAILLE_CELLS || dotIndex >= DOTS_PER_CELL) return;
  
  uint8_t absoluteDotIndex = cellIndex * DOTS_PER_CELL + dotIndex;
  setDotState(absoluteDotIndex, true, false);
}

// Lower specific dot
void BrailleDisplay::lowerDot(uint8_t cellIndex, uint8_t dotIndex) {
  if (cellIndex >= NUM_BRAILLE_CELLS || dotIndex >= DOTS_PER_CELL) return;
  
  uint8_t absoluteDotIndex = cellIndex * DOTS_PER_CELL + dotIndex;
  setDotState(absoluteDotIndex, false, false);
}

// Raise dot immediately
void BrailleDisplay::raiseDotImmediate(uint8_t cellIndex, uint8_t dotIndex) {
  if (cellIndex >= NUM_BRAILLE_CELLS || dotIndex >= DOTS_PER_CELL) return;
  
  uint8_t absoluteDotIndex = cellIndex * DOTS_PER_CELL + dotIndex;
  setDotState(absoluteDotIndex, true, true);
}

// Lower dot immediately
void BrailleDisplay::lowerDotImmediate(uint8_t cellIndex, uint8_t dotIndex) {
  if (cellIndex >= NUM_BRAILLE_CELLS || dotIndex >= DOTS_PER_CELL) return;
  
  uint8_t absoluteDotIndex = cellIndex * DOTS_PER_CELL + dotIndex;
  setDotState(absoluteDotIndex, false, true);
}

// Get current physical state of cell
uint8_t BrailleDisplay::getCurrentCellState(uint8_t cellIndex) const {
  if (!isValidBrailleCell(cellIndex)) {
    return 0;
  }
  return cells[cellIndex].currentState;
}

// Process pending dot actions
void BrailleDisplay::processPendingActions() {
  unsigned long currentTime = millis();
  bool updateNeeded = false;
  
  for (uint8_t i = 0; i < TOTAL_DOTS; i++) {
    if (dotStates[i].actionPending && currentTime >= dotStates[i].actionTime) {
      dotStates[i].currentState = dotStates[i].targetState;
      dotStates[i].actionPending = false;
      updateNeeded = true;
    }
  }
  
  if (updateNeeded) {
    updateShiftRegisters();
    if (displayEnabled) {
      refresh();
    }
  }
}

// Update function to call in main loop
void BrailleDisplay::update() {
  processPendingActions();
}

// Get output index for specific dot and direction
uint8_t BrailleDisplay::getDotOutputIndex(uint8_t dotIndex, uint8_t direction) {
  return (dotIndex * OUTPUTS_PER_DOT) + direction;
}

// Utility function: Mirror Braille pattern for writing
uint8_t mirrorBraillePattern(uint8_t pattern) {
  uint8_t mirrored = 0;
  
  // Mirror dots horizontally: 1<->4, 2<->5, 3<->6
  if (pattern & 0x01) mirrored |= 0x08; // dot 1 -> dot 4
  if (pattern & 0x02) mirrored |= 0x10; // dot 2 -> dot 5
  if (pattern & 0x04) mirrored |= 0x20; // dot 3 -> dot 6
  if (pattern & 0x08) mirrored |= 0x01; // dot 4 -> dot 1
  if (pattern & 0x10) mirrored |= 0x02; // dot 5 -> dot 2
  if (pattern & 0x20) mirrored |= 0x04; // dot 6 -> dot 3
  
  return mirrored;
}

// Utility function: Check if cell index is valid
bool isValidBrailleCell(uint8_t cellIndex) {
  return cellIndex < NUM_BRAILLE_CELLS;
}

// Utility function: Convert pattern to string representation
String patternToString(uint8_t pattern) {
  String result = "";
  for (uint8_t i = 0; i < DOTS_PER_CELL; i++) {
    if (pattern & (1 << i)) {
      if (result.length() > 0) result += ",";
      result += String(i + 1);
    }
  }
  return result.length() > 0 ? result : "none";
}