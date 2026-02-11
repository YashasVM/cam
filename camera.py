#!/usr/bin/env python3
"""
Omarchy Camera - A simple camera application for Linux
"""

import gi
import sys
import os
from datetime import datetime
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gtk, Gst, GLib, Gdk, GstVideo

Gst.init(None)


class CameraWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(800, 600)
        self.set_title("Omarchy Camera")

        # Setup save directory
        self.save_dir = Path.home() / "Pictures" / "Camera"
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Create GStreamer pipeline
        self.setup_pipeline()

        # Create UI
        self.setup_ui()

    def setup_pipeline(self):
        """Setup GStreamer pipeline for camera capture"""
        # Pipeline: camera -> tee (split) -> queue -> display
        #                      |-> queue -> encoder -> filesink

        self.pipeline = Gst.Pipeline.new("camera-pipeline")

        # Source
        self.source = Gst.ElementFactory.make("v4l2src", "source")
        if not self.source:
            self.source = Gst.ElementFactory.make("autovideosrc", "source")

        # Converter and scaling
        self.videoconvert = Gst.ElementFactory.make("videoconvert", "convert")
        self.videoscale = Gst.ElementFactory.make("videoscale", "scale")

        # Caps filter for resolution
        caps = Gst.Caps.from_string("video/x-raw,width=1280,height=720")
        self.capsfilter = Gst.ElementFactory.make("capsfilter", "caps")
        self.capsfilter.set_property("caps", caps)

        # Tee to split stream
        self.tee = Gst.ElementFactory.make("tee", "tee")

        # Display branch
        self.queue1 = Gst.ElementFactory.make("queue", "queue1")
        self.sink = Gst.ElementFactory.make("gtk4paintablesink", "sink")
        if not self.sink:
            self.sink = Gst.ElementFactory.make("autovideosink", "sink")

        # Add elements to pipeline
        elements = [
            self.source, self.videoconvert, self.videoscale,
            self.capsfilter, self.tee, self.queue1, self.sink
        ]

        for element in elements:
            if not element:
                print("Failed to create GStreamer element")
                sys.exit(1)
            self.pipeline.add(element)

        # Link elements
        if not (self.source.link(self.videoconvert) and
                self.videoconvert.link(self.videoscale) and
                self.videoscale.link(self.capsfilter) and
                self.capsfilter.link(self.tee) and
                self.tee.link(self.queue1) and
                self.queue1.link(self.sink)):
            print("Failed to link GStreamer elements")
            sys.exit(1)

        # Get paintable for GTK
        if hasattr(self.sink.props, 'paintable'):
            self.paintable = self.sink.props.paintable
        else:
            self.paintable = None

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(box)

        # Video display
        if self.paintable:
            self.video_area = Gtk.Picture.new_for_paintable(self.paintable)
            self.video_area.set_vexpand(True)
            self.video_area.set_hexpand(True)
        else:
            self.video_area = Gtk.Label(label="Camera preview not available")
            self.video_area.set_vexpand(True)

        box.append(self.video_area)

        # Control bar
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        control_box.set_margin_start(10)
        control_box.set_margin_end(10)
        control_box.set_margin_top(10)
        control_box.set_margin_bottom(10)
        control_box.set_halign(Gtk.Align.CENTER)

        # Capture button
        self.capture_btn = Gtk.Button(label="📷 Take Photo")
        self.capture_btn.set_size_request(150, 50)
        self.capture_btn.connect("clicked", self.on_capture)
        self.capture_btn.add_css_class("suggested-action")
        control_box.append(self.capture_btn)

        # Recording button
        self.record_btn = Gtk.Button(label="🔴 Record Video")
        self.record_btn.set_size_request(150, 50)
        self.record_btn.connect("clicked", self.on_record)
        control_box.append(self.record_btn)

        # Status label
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_margin_start(20)
        control_box.append(self.status_label)

        box.append(control_box)

        # Recording state
        self.is_recording = False
        self.record_pipeline = None

    def start_camera(self):
        """Start the camera preview"""
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop_camera(self):
        """Stop the camera preview"""
        self.pipeline.set_state(Gst.State.NULL)
        if self.record_pipeline:
            self.record_pipeline.set_state(Gst.State.NULL)

    def on_capture(self, button):
        """Capture a photo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"photo_{timestamp}.jpg"

        # Create a snapshot pipeline
        snap_pipeline = Gst.parse_launch(
            f'v4l2src num-buffers=1 ! videoconvert ! jpegenc ! filesink location="{filename}"'
        )

        # Set up bus to monitor completion
        bus = snap_pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_snapshot_message, snap_pipeline, filename)

        snap_pipeline.set_state(Gst.State.PLAYING)
        self.status_label.set_text("Capturing...")

    def on_snapshot_message(self, bus, message, pipeline, filename):
        """Handle snapshot pipeline messages"""
        if message.type == Gst.MessageType.EOS:
            pipeline.set_state(Gst.State.NULL)
            self.status_label.set_text(f"Photo saved: {filename.name}")
            GLib.timeout_add_seconds(3, lambda: self.status_label.set_text("Ready"))
        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            pipeline.set_state(Gst.State.NULL)
            self.status_label.set_text(f"Error: {err.message}")
            print(f"Error: {err.message}")

    def on_record(self, button):
        """Toggle video recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start video recording"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.save_dir / f"video_{timestamp}.mp4"

        # Create recording pipeline
        pipeline_str = f'''
            v4l2src ! videoconvert ! videoscale !
            video/x-raw,width=1280,height=720 !
            x264enc tune=zerolatency bitrate=2000 !
            mp4mux ! filesink location="{filename}"
        '''

        self.record_pipeline = Gst.parse_launch(pipeline_str)
        self.record_pipeline.set_state(Gst.State.PLAYING)

        self.is_recording = True
        self.record_btn.set_label("⏹️  Stop Recording")
        self.record_btn.remove_css_class("suggested-action")
        self.record_btn.add_css_class("destructive-action")
        self.status_label.set_text(f"Recording: {filename.name}")

    def stop_recording(self):
        """Stop video recording"""
        if self.record_pipeline:
            self.record_pipeline.send_event(Gst.Event.new_eos())
            GLib.timeout_add(500, self.cleanup_recording)

        self.is_recording = False
        self.record_btn.set_label("🔴 Record Video")
        self.record_btn.remove_css_class("destructive-action")
        self.record_btn.add_css_class("suggested-action")

    def cleanup_recording(self):
        """Cleanup after recording stops"""
        if self.record_pipeline:
            self.record_pipeline.set_state(Gst.State.NULL)
            self.record_pipeline = None
        self.status_label.set_text("Recording saved")
        GLib.timeout_add_seconds(3, lambda: self.status_label.set_text("Ready"))
        return False


class CameraApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.omarchy.camera')

    def do_activate(self):
        win = CameraWindow(application=self)
        win.present()
        win.start_camera()

    def do_shutdown(self):
        # Stop camera when app closes
        windows = self.get_windows()
        for win in windows:
            if isinstance(win, CameraWindow):
                win.stop_camera()
        Gtk.Application.do_shutdown(self)


def main():
    app = CameraApp()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
