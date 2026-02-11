# Omarchy Camera 📷

A full-featured camera application for Linux with live preview, photo capture, and video recording. Built specifically for Omarchy (Arch-based Hyprland distro) but works on any Linux system.

![Screenshot](https://img.shields.io/badge/status-stable-green) ![Platform](https://img.shields.io/badge/platform-Linux-blue) ![License](https://img.shields.io/badge/license-MIT-lightgrey)

## ✨ Features

- 📸 **Photo Mode** - Instant high-quality photo capture
- 🎥 **Video Mode** - Record videos with live preview
- 👁️ **Live Preview** - Toggle camera preview on/off to save resources
- 🔄 **Mode Switching** - Easy toggle between photo and video modes
- 🎨 **Modern UI** - Clean Catppuccin-themed interface
- 💾 **Auto-save** - All media automatically saved to `~/Pictures/Camera`
- 🔴 **Recording Indicator** - Visual REC indicator during video recording
- ⚡ **Lightweight** - Uses OpenCV and Tkinter (minimal dependencies)

## 🚀 Quick Start

### Automatic Installation (Recommended)

```bash
git clone https://github.com/YashasVM/cam.git
cd cam
./install.sh
```

The installer will:
- Check system requirements
- Install dependencies (python-opencv, python-pillow, tk)
- Install the app to `/usr/local/bin/omarchy-camera`
- Add it to your application menu
- Check camera permissions

### Manual Installation

```bash
# 1. Install dependencies
sudo pacman -S python python-opencv python-pillow tk

# 2. Run directly
python3 camera.py

# OR install system-wide
sudo cp camera.py /usr/local/bin/omarchy-camera
sudo chmod +x /usr/local/bin/omarchy-camera
```

## 📖 Usage

### Launching

- **Terminal**: `omarchy-camera` or `python3 camera.py`
- **App Menu**: Search for "Omarchy Camera"

### Controls

1. **Mode Selection** (Top bar)
   - Click "📷 Photo" for photo mode
   - Click "🎥 Video" for video mode

2. **Preview Toggle**
   - Click "👁️ Preview ON/OFF" to toggle live preview
   - Turn off preview to save CPU when not actively using camera

3. **Capture Actions**
   - **Photo Mode**: Click "📷 CAPTURE" to take a photo (with flash effect)
   - **Video Mode**: Click "🔴 START RECORDING" to begin, "⏹️ STOP RECORDING" to finish

### File Output

- **Photos**: `~/Pictures/Camera/photo_YYYYMMDD_HHMMSS.jpg`
- **Videos**: `~/Pictures/Camera/video_YYYYMMDD_HHMMSS.avi`

## 🔧 System Check

Run the test script to verify your system:

```bash
./test-system.sh
```

This will check:
- Python installation
- Camera device availability
- Required Python modules

## 🛠️ Troubleshooting

### Camera not detected

```bash
# Check for camera devices
ls /dev/video*

# List all video devices
v4l2-ctl --list-devices

# Test camera with mpv
mpv av://v4l2:/dev/video0
```

### Permission denied

Add yourself to the `video` group:

```bash
sudo usermod -aG video $USER
```

Then **log out and log back in** for changes to take effect.

### Camera in use

Close other applications using the camera:
- Web browsers (video calls, camera tests)
- Video chat apps (Zoom, Teams, Discord)
- Other camera applications

### Dependency conflicts

If you get GStreamer version conflicts:

```bash
# Update system first
sudo pacman -Syu

# Then install dependencies
sudo pacman -S python python-opencv python-pillow tk
```

## 📋 Requirements

- **OS**: Linux (tested on Arch/Omarchy)
- **Python**: 3.8+
- **Dependencies**:
  - `python-opencv` - Camera capture and video processing
  - `python-pillow` - Image handling
  - `tk` - GUI framework
- **Hardware**: v4l2 compatible camera (most USB/built-in cameras)

## 🎯 Technical Details

- **Framework**: Python with Tkinter GUI
- **Video Backend**: OpenCV (cv2)
- **Video Codec**: XVID (AVI format, widely compatible)
- **Resolution**: 1280x720 @ 30fps (configurable in code)
- **Preview**: ~30fps live preview with 960x540 display
- **Theme**: Catppuccin Mocha colors

## 📁 Project Structure

```
cam/
├── camera.py              # Main application
├── camera.sh              # Bash alternative (ffmpeg-based)
├── install.sh             # Complete installer
├── test-system.sh         # System check script
├── omarchy-camera.desktop # Desktop entry
└── README.md             # This file
```

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built for the [Omarchy](https://omarchy.org) Linux distribution
- Uses [OpenCV](https://opencv.org/) for camera handling
- UI inspired by [Catppuccin](https://github.com/catppuccin/catppuccin) theme

---

**Made with ❤️ for Omarchy** 🐧

Need help? Open an issue on [GitHub](https://github.com/YashasVM/cam/issues)
