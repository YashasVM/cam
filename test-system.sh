#!/bin/bash
# Test script for Omarchy Camera

echo "==================================="
echo "  Omarchy Camera - System Check"
echo "==================================="
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python3 not found"
    exit 1
fi

# Check camera device
echo ""
echo "2. Checking camera device..."
if ls /dev/video* &> /dev/null; then
    echo "   ✅ Camera devices found:"
    ls /dev/video* | while read device; do
        echo "      - $device"
    done
else
    echo "   ❌ No camera device found at /dev/video*"
    echo "   Make sure your camera is connected"
fi

# Check Python modules
echo ""
echo "3. Checking Python dependencies..."

check_module() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "   ✅ $2"
        return 0
    else
        echo "   ❌ $2 (missing)"
        return 1
    fi
}

MISSING=0

check_module "cv2" "OpenCV (cv2)" || MISSING=1
check_module "PIL" "Pillow (PIL)" || MISSING=1
check_module "tkinter" "Tkinter" || MISSING=1

echo ""
if [ $MISSING -eq 1 ]; then
    echo "❌ Missing dependencies detected!"
    echo ""
    echo "Install with:"
    echo "  sudo pacman -S python python-opencv python-pillow tk"
    echo ""
    exit 1
else
    echo "✅ All dependencies installed!"
    echo ""
    echo "Ready to run: python3 camera.py"
fi
