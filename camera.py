#!/usr/bin/env python3
"""
Omarchy Camera - Simple camera app using OpenCV
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

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Omarchy Camera")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e2e')

        # Setup save directory
        self.save_dir = Path.home() / "Pictures" / "Camera"
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Camera setup
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("No camera found!")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # Recording state
        self.is_recording = False
        self.video_writer = None

        self.setup_ui()
        self.update_frame()

    def setup_ui(self):
        """Setup the user interface"""
        # Video frame
        self.video_frame = tk.Label(self.root, bg='black')
        self.video_frame.pack(pady=10, padx=10, expand=True, fill='both')

        # Control frame
        control_frame = tk.Frame(self.root, bg='#1e1e2e')
        control_frame.pack(pady=10)

        # Style for buttons
        style = ttk.Style()
        style.configure('Camera.TButton', font=('Sans', 12, 'bold'), padding=10)

        # Photo button
        self.photo_btn = tk.Button(
            control_frame,
            text="📷 Take Photo",
            command=self.take_photo,
            font=('Sans', 12, 'bold'),
            bg='#89b4fa',
            fg='black',
            activebackground='#74c7ec',
            width=15,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        self.photo_btn.grid(row=0, column=0, padx=10)

        # Video button
        self.video_btn = tk.Button(
            control_frame,
            text="🔴 Record Video",
            command=self.toggle_recording,
            font=('Sans', 12, 'bold'),
            bg='#f38ba8',
            fg='black',
            activebackground='#f5c2e7',
            width=15,
            height=2,
            relief='flat',
            cursor='hand2'
        )
        self.video_btn.grid(row=0, column=1, padx=10)

        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Ready",
            font=('Sans', 10),
            bg='#1e1e2e',
            fg='#cdd6f4'
        )
        self.status_label.grid(row=1, column=0, columnspan=2, pady=10)

    def update_frame(self):
        """Update video preview"""
        ret, frame = self.cap.read()
        if ret:
            # Write to video if recording
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)

            # Convert for display
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (800, 600))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)

        self.root.after(10, self.update_frame)

    def take_photo(self):
        """Capture a photo"""
        ret, frame = self.cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.save_dir / f"photo_{timestamp}.jpg"
            cv2.imwrite(str(filename), frame)
            self.status_label.config(text=f"Photo saved: {filename.name}")
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def toggle_recording(self):
        """Toggle video recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start video recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"video_{timestamp}.avi"

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            str(filename),
            fourcc,
            20.0,
            (int(self.cap.get(3)), int(self.cap.get(4)))
        )

        self.is_recording = True
        self.video_btn.config(text="⏹️  Stop Recording", bg='#a6e3a1')
        self.status_label.config(text=f"Recording: {filename.name}")

    def stop_recording(self):
        """Stop video recording"""
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.video_btn.config(text="🔴 Record Video", bg='#f38ba8')
        self.status_label.config(text="Recording saved")
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))

    def show_error(self, message):
        """Show error message"""
        error_label = tk.Label(
            self.root,
            text=f"❌ {message}",
            font=('Sans', 14),
            bg='#1e1e2e',
            fg='#f38ba8'
        )
        error_label.pack(expand=True)

    def cleanup(self):
        """Cleanup resources"""
        self.is_recording = False
        if self.video_writer:
            self.video_writer.release()
        if self.cap:
            self.cap.release()


def main():
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.cleanup(), root.destroy()])
    root.mainloop()


if __name__ == '__main__':
    main()
