/*
 * Braille Writing Slate - Arduino Mega
 * 
 * This code handles a 10x10 grid of tactile buttons (100 total)
 * representing a Braille writing slate. Each button press is detected
 * and the position is sent via serial to the main Arduino.
 * 
 * Hardware:
 * - Arduino Mega 2560
 * - 100 tactile buttons in 10x10 matrix
 * - Uses matrix scanning with pull-up resistors
 * 
 * Protocol:
 * Sends: "BTN:row,col" when button pressed
 * Sends: "REL:row,col" when button released
 * Receives: "LED:row,col,state" to control position LEDs (optional)
 */

#include <Arduino.h>

// Configuration
#define MATRIX_ROWS 10
#define MATRIX_COLS 10
#define DEBOUNCE_DELAY 50  // milliseconds
#define SCAN_DELAY 2       // microseconds between scans

// Pin assignments for matrix scanning
// Rows (outputs) - Digital pins 22-31 on Mega
const uint8_t rowPins[MATRIX_ROWS] = {22, 23, 24, 25, 26, 27, 28, 29, 30, 31};

// Columns (inputs with pull-ups) - Digital pins 32-41 on Mega
const uint8_t colPins[MATRIX_COLS] = {32, 33, 34, 35, 36, 37, 38, 39, 40, 41};

// Optional LED pins for position feedback (pins 42-51)
const uint8_t ledPins[MATRIX_ROWS] = {42, 43, 44, 45, 46, 47, 48, 49, 50, 51};

// Button state tracking
bool buttonState[MATRIX_ROWS][MATRIX_COLS];
bool lastButtonState[MATRIX_ROWS][MATRIX_COLS];
unsigned long lastDebounceTime[MATRIX_ROWS][MATRIX_COLS];

// Current position tracking
int8_t currentRow = -1;
int8_t currentCol = -1;
bool positionActive = false;

// Communication
String inputBuffer = "";
bool stringComplete = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize matrix pins
  initializeMatrix();
  
  // Initialize button states
  initializeButtonStates();
  
  // Initialize LEDs
  initializeLEDs();
  
  Serial.println(F("Braille Writing Slate Ready"));
  Serial.println(F("Matrix: 10x10 (100 buttons)"));
  Serial.println(F("Protocol: BTN:row,col / REL:row,col"));
  
  // Flash all LEDs to indicate ready
  flashStartupSequence();
}

void loop() {
  // Scan button matrix
  scanMatrix();
  
  // Process any incoming serial commands
  processSerialCommands();
  
  // Small delay to prevent excessive scanning
  delayMicroseconds(SCAN_DELAY);
}

void initializeMatrix() {
  // Configure row pins as outputs
  for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
    pinMode(rowPins[row], OUTPUT);
    digitalWrite(rowPins[row], HIGH); // Start with all rows HIGH
  }
  
  // Configure column pins as inputs with pull-ups
  for (uint8_t col = 0; col < MATRIX_COLS; col++) {
    pinMode(colPins[col], INPUT_PULLUP);
  }
  
  Serial.println(F("Matrix pins initialized"));
}

void initializeButtonStates() {
  for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
    for (uint8_t col = 0; col < MATRIX_COLS; col++) {
      buttonState[row][col] = false;
      lastButtonState[row][col] = false;
      lastDebounceTime[row][col] = 0;
    }
  }
  
  Serial.println(F("Button states initialized"));
}

void initializeLEDs() {
  // Configure LED pins as outputs
  for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }
  
  Serial.println(F("LED pins initialized"));
}

void flashStartupSequence() {
  // Flash all LEDs in sequence
  for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
    digitalWrite(ledPins[i], HIGH);
    delay(100);
    digitalWrite(ledPins[i], LOW);
  }
  
  // Flash all together
  for (uint8_t flash = 0; flash < 3; flash++) {
    for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
      digitalWrite(ledPins[i], HIGH);
    }
    delay(200);
    for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
      digitalWrite(ledPins[i], LOW);
    }
    delay(200);
  }
}

void scanMatrix() {
  for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
    // Set current row LOW (active)
    digitalWrite(rowPins[row], LOW);
    
    // Small delay for signal to stabilize
    delayMicroseconds(10);
    
    // Read all columns for this row
    for (uint8_t col = 0; col < MATRIX_COLS; col++) {
      bool reading = !digitalRead(colPins[col]); // Inverted due to pull-up
      
      // Check if state changed
      if (reading != lastButtonState[row][col]) {
        lastDebounceTime[row][col] = millis();
      }
      
      // Debounce check
      if ((millis() - lastDebounceTime[row][col]) > DEBOUNCE_DELAY) {
        if (reading != buttonState[row][col]) {
          buttonState[row][col] = reading;
          
          // Send button event
          if (reading) {
            sendButtonPress(row, col);
          } else {
            sendButtonRelease(row, col);
          }
        }
      }
      
      lastButtonState[row][col] = reading;
    }
    
    // Set row back to HIGH (inactive)
    digitalWrite(rowPins[row], HIGH);
  }
}

void sendButtonPress(uint8_t row, uint8_t col) {
  Serial.print(F("BTN:"));
  Serial.print(row);
  Serial.print(F(","));
  Serial.println(col);
  
  // Update current position
  currentRow = row;
  currentCol = col;
  positionActive = true;
  
  // Light up position LED
  if (row < MATRIX_ROWS) {
    digitalWrite(ledPins[row], HIGH);
  }
  
  // Debug output
  Serial.print(F("Button pressed at ("));
  Serial.print(row);
  Serial.print(F(","));
  Serial.print(col);
  Serial.println(F(")"));
}

void sendButtonRelease(uint8_t row, uint8_t col) {
  Serial.print(F("REL:"));
  Serial.print(row);
  Serial.print(F(","));
  Serial.println(col);
  
  // Turn off position LED
  if (row < MATRIX_ROWS) {
    digitalWrite(ledPins[row], LOW);
  }
  
  // Clear current position if this was the active button
  if (currentRow == row && currentCol == col) {
    currentRow = -1;
    currentCol = -1;
    positionActive = false;
  }
  
  // Debug output
  Serial.print(F("Button released at ("));
  Serial.print(row);
  Serial.print(F(","));
  Serial.print(col);
  Serial.println(F(")"));
}

void processSerialCommands() {
  // Read serial input
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputBuffer += inChar;
    
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  
  // Process complete command
  if (stringComplete) {
    inputBuffer.trim();
    processCommand(inputBuffer);
    inputBuffer = "";
    stringComplete = false;
  }
}

void processCommand(String command) {
  if (command.startsWith("LED:")) {
    // LED control command: LED:row,col,state
    int firstComma = command.indexOf(',');
    int secondComma = command.indexOf(',', firstComma + 1);
    
    if (firstComma > 0 && secondComma > 0) {
      uint8_t row = command.substring(4, firstComma).toInt();
      uint8_t col = command.substring(firstComma + 1, secondComma).toInt();
      uint8_t state = command.substring(secondComma + 1).toInt();
      
      setLED(row, col, state);
    }
  } else if (command.startsWith("TEST")) {
    // Test command
    runTestSequence();
  } else if (command.startsWith("STATUS")) {
    // Status request
    sendStatus();
  } else if (command.startsWith("RESET")) {
    // Reset command
    resetState();
  } else {
    Serial.print(F("Unknown command: "));
    Serial.println(command);
  }
}

void setLED(uint8_t row, uint8_t col, uint8_t state) {
  if (row < MATRIX_ROWS) {
    digitalWrite(ledPins[row], state ? HIGH : LOW);
    
    Serial.print(F("LED ("));
    Serial.print(row);
    Serial.print(F(","));
    Serial.print(col);
    Serial.print(F(") set to "));
    Serial.println(state ? F("ON") : F("OFF"));
  }
}

void runTestSequence() {
  Serial.println(F("Running test sequence..."));
  
  // Test all LEDs
  for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
    digitalWrite(ledPins[i], HIGH);
    delay(200);
    digitalWrite(ledPins[i], LOW);
  }
  
  // Test matrix scanning by simulating button presses
  Serial.println(F("Matrix test - press any button"));
  
  unsigned long testStart = millis();
  while (millis() - testStart < 5000) { // 5 second test
    scanMatrix();
    delay(10);
  }
  
  Serial.println(F("Test sequence complete"));
}

void sendStatus() {
  Serial.println(F("=== Braille Writing Slate Status ==="));
  Serial.print(F("Matrix size: "));
  Serial.print(MATRIX_ROWS);
  Serial.print(F("x"));
  Serial.println(MATRIX_COLS);
  
  Serial.print(F("Current position: "));
  if (positionActive) {
    Serial.print(F("("));
    Serial.print(currentRow);
    Serial.print(F(","));
    Serial.print(currentCol);
    Serial.println(F(")"));
  } else {
    Serial.println(F("None"));
  }
  
  Serial.print(F("Active buttons: "));
  uint8_t activeCount = 0;
  for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
    for (uint8_t col = 0; col < MATRIX_COLS; col++) {
      if (buttonState[row][col]) {
        if (activeCount > 0) Serial.print(F(", "));
        Serial.print(F("("));
        Serial.print(row);
        Serial.print(F(","));
        Serial.print(col);
        Serial.print(F(")"));
        activeCount++;
      }
    }
  }
  if (activeCount == 0) {
    Serial.println(F("None"));
  } else {
    Serial.println();
  }
  
  Serial.println(F("================================"));
}

void resetState() {
  Serial.println(F("Resetting state..."));
  
  // Clear all button states
  initializeButtonStates();
  
  // Turn off all LEDs
  for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
    digitalWrite(ledPins[i], LOW);
  }
  
  // Clear position tracking
  currentRow = -1;
  currentCol = -1;
  positionActive = false;
  
  Serial.println(F("State reset complete"));
}

// Interrupt service routine for emergency stop (optional)
void emergencyStop() {
  // Turn off all LEDs
  for (uint8_t i = 0; i < MATRIX_ROWS; i++) {
    digitalWrite(ledPins[i], LOW);
  }
  
  Serial.println(F("EMERGENCY STOP"));
}

// Function to map button position to Braille cell and dot
void mapButtonToBraille(uint8_t row, uint8_t col, uint8_t* cellIndex, uint8_t* dotIndex) {
  // Each Braille cell occupies a 2x3 area in the button matrix
  // 10 columns allows for 3 cells per row (with spacing)
  // 10 rows allows for 3 complete rows of Braille cells
  
  *cellIndex = (row / 4) * 3 + (col / 3);
  
  // Map position within cell to dot number (1-6)
  uint8_t localRow = row % 4;
  uint8_t localCol = col % 3;
  
  if (localRow < 3 && localCol < 2) {
    *dotIndex = localRow * 2 + localCol + 1;
  } else {
    *dotIndex = 0; // Invalid dot position
  }
}

// Function to get Braille pattern from button presses in a cell
uint8_t getBrailleCellPattern(uint8_t cellIndex) {
  uint8_t pattern = 0;
  uint8_t baseRow = (cellIndex / 3) * 4;
  uint8_t baseCol = (cellIndex % 3) * 3;
  
  // Check each dot position in the cell
  for (uint8_t dot = 1; dot <= 6; dot++) {
    uint8_t dotRow = baseRow + ((dot - 1) / 2);
    uint8_t dotCol = baseCol + ((dot - 1) % 2);
    
    if (dotRow < MATRIX_ROWS && dotCol < MATRIX_COLS) {
      if (buttonState[dotRow][dotCol]) {
        pattern |= (1 << (dot - 1));
      }
    }
  }
  
  return pattern;
}