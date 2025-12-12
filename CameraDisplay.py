# camera_worker.py - Simple camera display without CV processing
import cv2
from datetime import datetime
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class CameraWorker(QThread):
    image_data = pyqtSignal(QImage)
    file_saved = pyqtSignal(str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.thread_active = True
        self.is_frozen = False
        self.is_recording = False
        self.video_writer = None  
        self.current_frame = None
        self.frozen_frame = None
        
        # Create folders for saving files
        self.image_folder = "captured_images"
        self.video_folder = "recorded_videos"
        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.video_folder, exist_ok=True)

    def run(self):
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print(f"Error: Cannot open camera {self.camera_index}")
            return

        while self.thread_active:
            if not self.is_frozen:
                ret, frame = cap.read()
                if not ret:
                    continue

                # NO COMPUTER VISION - Just display raw frame
                self.current_frame = frame.copy()
                
                # Write to video if recording
                if self.is_recording and self.video_writer is not None:
                    self.video_writer.write(frame)
                
                # Convert to QImage and emit
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                bytes_per_line = ch * w
                qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.image_data.emit(qimg)
            else:
                # Display frozen frame
                if self.frozen_frame is not None:
                    rgb = cv2.cvtColor(self.frozen_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb.shape
                    bytes_per_line = ch * w
                    qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.image_data.emit(qimg)

        cap.release()
        if self.video_writer is not None:
            self.video_writer.release()

    def toggle_freeze(self):
        """Freeze or unfreeze the camera feed"""
        self.is_frozen = not self.is_frozen
        if self.is_frozen and self.current_frame is not None:
            self.frozen_frame = self.current_frame.copy()

    def capture_frame(self):
        """Save current frame as image"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cam{self.camera_index}_capture_{timestamp}.jpg"
            filepath = os.path.join(self.image_folder, filename)
            cv2.imwrite(filepath, self.current_frame)
            self.file_saved.emit(filepath)
            print(f"Frame saved: {filepath}")

    def toggle_recording(self):
        """Start or stop video recording"""
        if not self.is_recording:
            # Start recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cam{self.camera_index}_video_{timestamp}.avi"
            filepath = os.path.join(self.video_folder, filename)
            
            if self.current_frame is not None:
                height, width = self.current_frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.video_writer = cv2.VideoWriter(filepath, fourcc, 20.0, (width, height))
                self.is_recording = True
                print(f"Recording started: {filepath}")
                return filepath
        else:
            # Stop recording
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
            self.is_recording = False
            print("Recording stopped")
        return None

    def stop(self):
        self.thread_active = False
        if self.is_recording and self.video_writer is not None:
            self.video_writer.release()
        self.quit()
        self.wait()