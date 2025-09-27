# 🔹 Braille Writing Tutor

<div align="center">

![Braille](https://img.shields.io/badge/Accessibility-Braille-blue)
![Arduino](https://img.shields.io/badge/Arduino-00979D?style=flat&logo=Arduino&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/-RaspberryPi-C51A4A?style=flat&logo=Raspberry-Pi)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=flat&logo=c%2B%2B&logoColor=white)

*An innovative educational tool designed to help users learn Braille writing through interactive technology*

[Features](#-features) •
[Hardware](#-hardware-components) •
[Installation](#-installation) •
[Usage](#-usage) •
[Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Hardware Components](#-hardware-components)
- [Software Architecture](#-software-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Circuit Diagram](#-circuit-diagram)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## 🎯 Overview

The **Braille Writing Tutor** is an assistive technology project that combines hardware and software to create an interactive learning environment for Braille writing. This system uses Arduino microcontrollers and Raspberry Pi to provide tactile feedback and real-time guidance for users learning to write in Braille.

### 🎨 Key Objectives

- **Educational**: Provide an interactive way to learn Braille writing
- **Accessible**: Make Braille education more engaging and effective
- **Affordable**: Use common, cost-effective hardware components
- **Extensible**: Modular design for easy customization and expansion

## ✨ Features

### 🔧 Hardware Features
- **Tactile Feedback System**: Physical Braille cell simulation
- **Arduino-based Control**: Precise motor and sensor control
- **Raspberry Pi Integration**: Advanced processing and connectivity
- **Modular Design**: Easy to assemble and modify

### 💻 Software Features
- **Interactive Learning Modules**: Step-by-step Braille writing tutorials
- **Real-time Feedback**: Immediate correction and guidance
- **Progress Tracking**: Monitor learning advancement
- **Customizable Lessons**: Adaptable difficulty levels

### 🌐 System Features
- **Cross-platform Compatibility**: Works on multiple operating systems
- **Extensible Architecture**: Easy to add new features
- **Open Source**: Community-driven development

## 🛠 Hardware Components

### Required Components
- **Arduino Uno/Nano**: Main microcontroller
- **Raspberry Pi 4**: Central processing unit
- **Servo Motors**: For tactile feedback mechanism
- **Sensors**: Touch and position sensors
- **Braille Cell Assembly**: Physical Braille dot matrix
- **Power Supply**: 5V/12V power management
- **Connecting Wires**: Jumper wires and breadboard

### Optional Components
- **LCD Display**: Visual feedback (for instructors)
- **Speaker**: Audio feedback system
- **LED Indicators**: Status and progress indicators

## 🏗 Software Architecture

```
Braille Writing Tutor
├── Arduino Firmware (C++)
│   ├── Sensor Management
│   ├── Motor Control
│   └── Serial Communication
│
└── Raspberry Pi Application (Python)
    ├── User Interface
    ├── Learning Engine
    ├── Progress Tracking
    └── Arduino Communication
```

## 📁 Project Structure

```
BRAILLE WRITING TUTOR/
├── 📄 README.md                    # Project documentation
├── 📁 source/                      # Source code directory
│   ├── 📁 arduino/                 # Arduino firmware
│   │   └── 📁 BrailleWritingTutor/ # Main Arduino project
│   │       └── 📄 BrailleWritingTutor.ino
│   └── 📁 rpi/                     # Raspberry Pi software
│       └── 📁 BrailleWritingTutor/ # Main Python application
│           └── 📄 main.py
├── 📁 diagram/                     # Circuit diagrams and schematics
│   ├── 📄 Wiring.fzz              # Fritzing circuit file
│   └── 🖼 Wiring_bb.png           # Breadboard wiring diagram
└── 📁 model/                       # 3D models and mechanical designs
```

## 🚀 Installation

### Prerequisites

#### For Arduino Development
- Arduino IDE 1.8+ or Arduino CLI
- USB cable (Type-A to Type-B)
- Required Arduino libraries (listed in code)

#### For Raspberry Pi Development
```bash
# System requirements
- Raspberry Pi OS (Bullseye or newer)
- Python 3.8+
- GPIO access permissions
```

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/qppd/Braille-Writing-Tutor.git
cd Braille-Writing-Tutor
```

#### 2. Arduino Setup
```bash
# Navigate to Arduino source
cd source/arduino/BrailleWritingTutor

# Open in Arduino IDE or compile with CLI
arduino-cli compile --fqbn arduino:avr:uno BrailleWritingTutor.ino

# Upload to Arduino
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno
```

#### 3. Raspberry Pi Setup
```bash
# Navigate to Python source
cd source/rpi/BrailleWritingTutor

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # Create this file as needed

# Run the application
python3 main.py
```

#### 4. Hardware Assembly
1. Follow the circuit diagram in `diagram/Wiring_bb.png`
2. Connect Arduino to Raspberry Pi via USB
3. Wire sensors and actuators as shown in the schematic
4. Ensure proper power supply connections

## 🎮 Usage

### Basic Operation

1. **Power On**: Connect power to both Arduino and Raspberry Pi
2. **Initialize**: Run the Python application on Raspberry Pi
3. **Calibrate**: Follow on-screen calibration instructions
4. **Learn**: Start with basic Braille character tutorials
5. **Practice**: Use guided writing exercises
6. **Progress**: Track learning advancement

### Learning Modes

- **Tutorial Mode**: Step-by-step character learning
- **Practice Mode**: Free-form writing practice  
- **Test Mode**: Assessment and evaluation
- **Custom Mode**: User-defined lessons

## 📊 Circuit Diagram

![Wiring Diagram](diagram/Wiring_bb.png)

*Complete wiring schematic showing connections between Arduino, Raspberry Pi, sensors, and actuators. The Fritzing source file is available at `diagram/Wiring.fzz`.*

## 🔧 Development

### Contributing to the Project

We welcome contributions! Here's how to get started:

#### Development Environment Setup
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Braille-Writing-Tutor.git

# Create a feature branch
git checkout -b feature/amazing-new-feature

# Make your changes and commit
git commit -m "Add amazing new feature"

# Push to your fork and create a Pull Request
git push origin feature/amazing-new-feature
```

#### Code Style Guidelines
- **Arduino**: Follow Arduino style guide
- **Python**: PEP 8 compliance
- **Documentation**: Clear comments and docstrings
- **Commits**: Descriptive commit messages

### Future Enhancements

- [ ] **Multi-language Support**: Support for different Braille standards
- [ ] **Mobile App**: Companion mobile application
- [ ] **Cloud Sync**: Progress synchronization across devices
- [ ] **Advanced Analytics**: Detailed learning analytics
- [ ] **Voice Integration**: Voice-guided tutorials
- [ ] **Wireless Connectivity**: Bluetooth/WiFi communication

## 🤝 Contributing

We encourage community contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Ways to Contribute
- 🐛 **Bug Reports**: Found an issue? Let us know!
- 💡 **Feature Requests**: Suggest new functionality
- 📝 **Documentation**: Improve guides and tutorials
- 🔧 **Code**: Submit bug fixes and new features
- 🎨 **Design**: UI/UX improvements and hardware designs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sajed Qashqai**
- 🌐 GitHub: [@qppd](https://github.com/qppd)
- 📧 Email: Available on GitHub profile
- 🔗 Portfolio: Check GitHub repositories for more projects

---

<div align="center">

**⭐ If you found this project helpful, please give it a star! ⭐**

Made with ❤️ for accessibility and education

</div>
