#!/bin/bash
# Complete installer for Omarchy Camera

set -e

echo "╔═══════════════════════════════════════╗"
echo "║   Omarchy Camera - Full Installer    ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Don't run this as root (no sudo)"
    exit 1
fi

# Step 1: System check
echo "📋 Step 1: System Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

if ! ls /dev/video* &> /dev/null; then
    echo "⚠️  Warning: No camera detected at /dev/video*"
    echo "   Make sure camera is connected"
else
    echo "✅ Camera detected: $(ls /dev/video* | head -1)"
fi

# Step 2: Update system (optional, handle conflicts)
echo ""
echo "📦 Step 2: Installing Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This will install: python-opencv, python-pillow, tk"
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Try to install dependencies
echo "Installing packages..."
if sudo pacman -S --needed --noconfirm python python-opencv python-pillow tk; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some packages may have conflicts"
    echo ""
    echo "Try manually:"
    echo "  sudo pacman -Syu  # Update system first"
    echo "  sudo pacman -S python python-opencv python-pillow tk"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 3: Verify installation
echo ""
echo "🔍 Step 3: Verifying Installation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

VERIFY_FAILED=0

if python3 -c "import cv2" 2>/dev/null; then
    echo "✅ OpenCV"
else
    echo "❌ OpenCV not available"
    VERIFY_FAILED=1
fi

if python3 -c "import PIL" 2>/dev/null; then
    echo "✅ Pillow"
else
    echo "❌ Pillow not available"
    VERIFY_FAILED=1
fi

if python3 -c "import tkinter" 2>/dev/null; then
    echo "✅ Tkinter"
else
    echo "❌ Tkinter not available"
    VERIFY_FAILED=1
fi

if [ $VERIFY_FAILED -eq 1 ]; then
    echo ""
    echo "❌ Verification failed. Some dependencies missing."
    echo "   You can still try running: python3 camera.py"
    exit 1
fi

# Step 4: Install app
echo ""
echo "📲 Step 4: Installing Application"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Make camera.py executable
chmod +x camera.py

# Install to /usr/local/bin
echo "Installing to /usr/local/bin/omarchy-camera..."
sudo cp camera.py /usr/local/bin/omarchy-camera
sudo chmod +x /usr/local/bin/omarchy-camera
echo "✅ Installed to /usr/local/bin/omarchy-camera"

# Desktop integration
echo "Adding to application menu..."
mkdir -p ~/.local/share/applications
cp omarchy-camera.desktop ~/.local/share/applications/
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
fi
echo "✅ Added to application menu"

# Create save directory
mkdir -p ~/Pictures/Camera
echo "✅ Created save directory: ~/Pictures/Camera"

# Check video group membership
echo ""
echo "👥 Checking video group membership..."
if groups | grep -q video; then
    echo "✅ You're in the video group"
else
    echo "⚠️  You're not in the video group"
    echo "   This may cause camera access issues"
    echo ""
    read -p "Add yourself to video group? (requires logout) (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo usermod -aG video $USER
        echo "✅ Added to video group"
        echo "⚠️  You must LOG OUT and LOG BACK IN for this to take effect"
    fi
fi

# Done!
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║          ✅ Installation Complete!    ║"
echo "╚═══════════════════════════════════════╝"
echo ""
echo "Launch the app:"
echo "  📱 Command line: omarchy-camera"
echo "  📱 App menu: Search for 'Omarchy Camera'"
echo "  📱 Direct: python3 camera.py"
echo ""
echo "Photos/Videos save to: ~/Pictures/Camera"
echo ""
