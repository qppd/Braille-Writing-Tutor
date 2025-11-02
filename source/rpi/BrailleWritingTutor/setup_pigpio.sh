#!/bin/bash
# Setup script for pigpio on Raspberry Pi

echo "========================================="
echo "Braille Writing Tutor - pigpio Setup"
echo "========================================="
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Continuing anyway..."
    echo ""
fi

# Install pigpio
echo "Step 1: Installing pigpio..."
sudo apt update
sudo apt install -y pigpio python3-pigpio

# Enable pigpiod service
echo ""
echo "Step 2: Enabling pigpiod service..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# Check if pigpiod is running
echo ""
echo "Step 3: Checking pigpiod status..."
if sudo systemctl is-active --quiet pigpiod; then
    echo "✓ pigpiod is running"
else
    echo "✗ pigpiod failed to start"
    echo "  Trying to start manually..."
    sudo pigpiod
    sleep 2
    if pgrep pigpiod > /dev/null; then
        echo "✓ pigpiod started manually"
    else
        echo "✗ Failed to start pigpiod"
        exit 1
    fi
fi

# Add user to gpio group
echo ""
echo "Step 4: Adding user to gpio group..."
sudo usermod -a -G gpio $USER
echo "✓ User added to gpio group (logout/login required for effect)"

# Install Python package
echo ""
echo "Step 5: Installing Python pigpio package..."
if [ -d "venv" ]; then
    echo "  Found virtual environment, activating..."
    source venv/bin/activate
    pip install pigpio
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "  Virtual environment already active"
    pip install pigpio
else
    echo "  No virtual environment found, installing globally..."
    pip3 install pigpio
fi

# Test connection
echo ""
echo "Step 6: Testing pigpio connection..."
python3 -c "import pigpio; pi = pigpio.pi(); print('✓ Connected to pigpiod!' if pi.connected else '✗ Connection failed'); pi.stop()"

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. If this is your first time, logout and login again"
echo "   (for gpio group membership to take effect)"
echo "2. Activate your virtual environment:"
echo "   source venv/bin/activate"
echo "3. Run the application:"
echo "   python main.py"
echo ""
echo "If you encounter any issues, check SETUP_PIGPIO.md"
echo ""
