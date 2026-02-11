#!/bin/bash
# Simple installer for Omarchy Camera

echo "🔧 Installing Omarchy Camera..."

# Install dependencies
echo "📦 Installing dependencies..."
sudo pacman -S --needed --noconfirm python python-opencv python-pillow tk

# Install app
echo "📲 Installing app..."
sudo cp camera.py /usr/local/bin/omarchy-camera
sudo chmod +x /usr/local/bin/omarchy-camera

# Desktop integration
echo "🖥️  Adding to app menu..."
mkdir -p ~/.local/share/applications
cp omarchy-camera.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/ 2>/dev/null

echo ""
echo "✅ Done! Launch with: omarchy-camera"
