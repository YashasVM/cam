# Omarchy Camera 📷

A simple, lightweight camera application for Linux (specifically built for Omarchy, an Arch-based Hyprland distro).

## Features

- 📸 Take photos
- 🎥 Record videos
- 🖼️ Live camera preview
- 💾 Auto-save to `~/Pictures/Camera`
- 🎨 Modern GTK4 interface
- 🌊 Wayland compatible

## Requirements

- Python 3
- GTK 4
- GStreamer with plugins
- v4l2 (Video4Linux2) for camera access

## Installation

### Arch Linux / Omarchy

```bash
sudo pacman -S python gtk4 gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-plugin-gtk python-gobject
```

### Other Distributions

**Debian/Ubuntu:**
```bash
sudo apt install python3 gir1.2-gtk-4.0 gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad python3-gi
```

**Fedora:**
```bash
sudo dnf install python3 gtk4 gstreamer1 gstreamer1-plugins-base gstreamer1-plugins-good gstreamer1-plugins-bad python3-gobject
```

## Usage

### Run the application

```bash
python3 camera.py
```

Or make it executable:

```bash
chmod +x camera.py
./camera.py
```

### Install system-wide (optional)

```bash
sudo cp camera.py /usr/local/bin/omarchy-camera
sudo chmod +x /usr/local/bin/omarchy-camera
```

Then run with:
```bash
omarchy-camera
```

## Desktop Integration

Create a `.desktop` file for application menu integration:

```bash
cp omarchy-camera.desktop ~/.local/share/applications/
```

## Controls

- **📷 Take Photo** - Capture a single photo
- **🔴 Record Video** - Start/stop video recording

All photos and videos are saved to `~/Pictures/Camera/`

## File Naming

- Photos: `photo_YYYYMMDD_HHMMSS.jpg`
- Videos: `video_YYYYMMDD_HHMMSS.mp4`

## Troubleshooting

### Camera not detected

Check if your camera is recognized:
```bash
ls /dev/video*
v4l2-ctl --list-devices
```

### Permission issues

Add your user to the `video` group:
```bash
sudo usermod -aG video $USER
```

Then log out and log back in.

### Missing GStreamer plugins

If you see errors about missing elements, install additional GStreamer plugins:
```bash
sudo pacman -S gst-libav gst-plugins-ugly
```

## License

MIT License - feel free to use, modify, and distribute!

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

Made for [Omarchy](https://github.com/omarchy) 🐧
