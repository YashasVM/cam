#!/usr/bin/env python3
"""
Omarchy Camera - Full-featured camera app
Photo mode, Video mode, Live preview
"""

import cv2
import sys
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Omarchy Camera")
        self.root.geometry("1000x750")
        self.root.configure(bg='#1e1e2e')

        # Setup save directory
        self.save_dir = Path.home() / "Pictures" / "Camera"
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Camera setup
        self.cap = None
        self.init_camera()

        # State
        self.mode = "photo"  # photo or video
        self.is_recording = False
        self.video_writer = None
        self.preview_active = False

        self.setup_ui()

        if self.cap and self.cap.isOpened():
            self.start_preview()

    def init_camera(self):
        """Initialize camera with fallback"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture('/dev/video0')

            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
        except Exception as e:
            print(f"Camera init error: {e}")
            self.cap = None

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e1e2e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Top bar - Mode switcher
        top_bar = tk.Frame(main_frame, bg='#1e1e2e')
        top_bar.pack(fill='x', pady=(0, 10))

        mode_label = tk.Label(
            top_bar,
            text="MODE:",
            font=('Sans', 11, 'bold'),
            bg='#1e1e2e',
            fg='#cdd6f4'
        )
        mode_label.pack(side='left', padx=(0, 10))

        self.photo_mode_btn = tk.Button(
            top_bar,
            text="📷 Photo",
            command=lambda: self.switch_mode("photo"),
            font=('Sans', 11, 'bold'),
            bg='#89b4fa',
            fg='#1e1e2e',
            activebackground='#74c7ec',
            width=12,
            relief='flat',
            cursor='hand2',
            pady=8
        )
        self.photo_mode_btn.pack(side='left', padx=5)

        self.video_mode_btn = tk.Button(
            top_bar,
            text="🎥 Video",
            command=lambda: self.switch_mode("video"),
            font=('Sans', 11, 'bold'),
            bg='#313244',
            fg='#cdd6f4',
            activebackground='#45475a',
            width=12,
            relief='flat',
            cursor='hand2',
            pady=8
        )
        self.video_mode_btn.pack(side='left', padx=5)

        # Preview toggle
        self.preview_btn = tk.Button(
            top_bar,
            text="👁️  Preview ON",
            command=self.toggle_preview,
            font=('Sans', 10),
            bg='#a6e3a1',
            fg='#1e1e2e',
            activebackground='#94e2d5',
            width=12,
            relief='flat',
            cursor='hand2',
            pady=8
        )
        self.preview_btn.pack(side='right', padx=5)

        # Video display
        video_container = tk.Frame(main_frame, bg='black', relief='solid', borderwidth=2)
        video_container.pack(fill='both', expand=True)

        self.video_frame = tk.Label(video_container, bg='black', text="Camera Preview", fg='#6c7086', font=('Sans', 16))
        self.video_frame.pack(fill='both', expand=True, padx=2, pady=2)

        # Control panel
        control_panel = tk.Frame(main_frame, bg='#1e1e2e')
        control_panel.pack(fill='x', pady=(10, 0))

        # Main action button
        self.action_btn = tk.Button(
            control_panel,
            text="📷 CAPTURE",
            command=self.main_action,
            font=('Sans', 14, 'bold'),
            bg='#89b4fa',
            fg='#1e1e2e',
            activebackground='#74c7ec',
            width=20,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        self.action_btn.pack(pady=10)

        # Status bar
        status_frame = tk.Frame(main_frame, bg='#313244', relief='flat')
        status_frame.pack(fill='x', pady=(5, 0))

        self.status_label = tk.Label(
            status_frame,
            text="📁 Ready - Photos/Videos save to ~/Pictures/Camera",
            font=('Sans', 9),
            bg='#313244',
            fg='#cdd6f4',
            anchor='w',
            padx=10,
            pady=5
        )
        self.status_label.pack(fill='x')

    def switch_mode(self, mode):
        """Switch between photo and video mode"""
        if self.is_recording:
            self.stop_recording()

        self.mode = mode

        if mode == "photo":
            self.photo_mode_btn.config(bg='#89b4fa', fg='#1e1e2e')
            self.video_mode_btn.config(bg='#313244', fg='#cdd6f4')
            self.action_btn.config(text="📷 CAPTURE", bg='#89b4fa', activebackground='#74c7ec')
        else:
            self.video_mode_btn.config(bg='#f38ba8', fg='#1e1e2e')
            self.photo_mode_btn.config(bg='#313244', fg='#cdd6f4')
            self.action_btn.config(text="🔴 START RECORDING", bg='#f38ba8', activebackground='#eba0ac')

        self.update_status(f"Switched to {mode.upper()} mode")

    def toggle_preview(self):
        """Toggle camera preview on/off"""
        if self.preview_active:
            self.stop_preview()
            self.preview_btn.config(text="👁️  Preview OFF", bg='#313244', fg='#cdd6f4')
        else:
            self.start_preview()
            self.preview_btn.config(text="👁️  Preview ON", bg='#a6e3a1', fg='#1e1e2e')

    def start_preview(self):
        """Start live camera preview"""
        self.preview_active = True
        self.update_frame()

    def stop_preview(self):
        """Stop live camera preview"""
        self.preview_active = False
        self.video_frame.config(image='', text="Preview OFF", fg='#6c7086', font=('Sans', 16))

    def update_frame(self):
        """Update video preview frame"""
        if not self.preview_active or not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # Write to video if recording
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)

            # Convert for display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Resize to fit window
            height, width = frame.shape[:2]
            max_width = 960
            max_height = 540
            scale = min(max_width/width, max_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)

            frame = cv2.resize(frame, (new_width, new_height))

            # Add recording indicator
            if self.is_recording:
                cv2.circle(frame, (30, 30), 15, (255, 0, 0), -1)
                cv2.putText(frame, "REC", (55, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk, text="")

        if self.preview_active:
            self.root.after(33, self.update_frame)  # ~30fps

    def main_action(self):
        """Main action button - capture photo or toggle recording"""
        if self.mode == "photo":
            self.take_photo()
        else:
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()

    def take_photo(self):
        """Capture a photo"""
        if not self.cap or not self.cap.isOpened():
            self.update_status("❌ Error: Camera not available", error=True)
            return

        ret, frame = self.cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.save_dir / f"photo_{timestamp}.jpg"
            cv2.imwrite(str(filename), frame)
            self.update_status(f"✅ Photo saved: {filename.name}")

            # Flash effect
            self.video_frame.config(bg='white')
            self.root.after(100, lambda: self.video_frame.config(bg='black'))
        else:
            self.update_status("❌ Failed to capture photo", error=True)

    def start_recording(self):
        """Start video recording"""
        if not self.cap or not self.cap.isOpened():
            self.update_status("❌ Error: Camera not available", error=True)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"video_{timestamp}.avi"

        # Get camera properties
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Use XVID codec (widely compatible)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            str(filename),
            fourcc,
            20.0,
            (width, height)
        )

        if not self.video_writer.isOpened():
            self.update_status("❌ Failed to start recording", error=True)
            self.video_writer = None
            return

        self.is_recording = True
        self.action_btn.config(text="⏹️  STOP RECORDING", bg='#a6e3a1', activebackground='#94e2d5')
        self.update_status(f"🔴 Recording: {filename.name}")

        # Make sure preview is on while recording
        if not self.preview_active:
            self.start_preview()
            self.preview_btn.config(text="👁️  Preview ON", bg='#a6e3a1', fg='#1e1e2e')

    def stop_recording(self):
        """Stop video recording"""
        self.is_recording = False

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.action_btn.config(text="🔴 START RECORDING", bg='#f38ba8', activebackground='#eba0ac')
        self.update_status("✅ Recording saved")

    def update_status(self, message, error=False):
        """Update status bar"""
        color = '#f38ba8' if error else '#cdd6f4'
        self.status_label.config(text=message, fg=color)

        if not error:
            # Reset to default message after 5 seconds
            self.root.after(5000, lambda: self.status_label.config(
                text="📁 Ready - Photos/Videos save to ~/Pictures/Camera",
                fg='#cdd6f4'
            ))

    def cleanup(self):
        """Cleanup resources"""
        self.preview_active = False
        self.is_recording = False

        if self.video_writer:
            self.video_writer.release()

        if self.cap:
            self.cap.release()


def main():
    # Check if camera is available
    test_cap = cv2.VideoCapture(0)
    if not test_cap.isOpened():
        print("❌ Error: No camera detected!")
        print("Make sure your camera is connected and not in use by another application.")
        print("\nTroubleshooting:")
        print("  1. Check: ls /dev/video*")
        print("  2. Check: v4l2-ctl --list-devices")
        print("  3. Add yourself to video group: sudo usermod -aG video $USER")
        sys.exit(1)
    test_cap.release()

    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.cleanup(), root.destroy()])
    root.mainloop()


if __name__ == '__main__':
    main()
