#!/bin/bash
# Dead simple camera app using ffmpeg

SAVE_DIR="$HOME/Pictures/Camera"
mkdir -p "$SAVE_DIR"

echo "╔════════════════════════════════════╗"
echo "║     OMARCHY CAMERA                 ║"
echo "╚════════════════════════════════════╝"
echo ""
echo "1) 📷 Take Photo"
echo "2) 🎥 Record Video"
echo "3) 🖼️  Preview Camera"
echo "4) ❌ Exit"
echo ""
read -p "Choose: " choice

case $choice in
    1)
        FILE="$SAVE_DIR/photo_$(date +%Y%m%d_%H%M%S).jpg"
        ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 "$FILE" -y 2>/dev/null
        echo "✅ Photo saved: $FILE"
        ;;
    2)
        FILE="$SAVE_DIR/video_$(date +%Y%m%d_%H%M%S).mp4"
        echo "🔴 Recording... Press Ctrl+C to stop"
        ffmpeg -f v4l2 -i /dev/video0 -c:v libx264 -preset ultrafast "$FILE"
        echo "✅ Video saved: $FILE"
        ;;
    3)
        echo "👁️  Camera preview (press Q to quit)"
        mpv --no-cache --untimed --no-demuxer-thread --vf=hflip av://v4l2:/dev/video0
        ;;
    4)
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
