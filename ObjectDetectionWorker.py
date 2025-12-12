# ObjectDetectionWorker.py
import cv2
import numpy as np
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class ObjectDetectionWorker(QThread):
    image_data = pyqtSignal(QImage)

    def __init__(self, source=0):
        """
        source: int (camera index) or str (file path)
        """
        super().__init__()
        self.source = source
        self.thread_active = True

    def run(self):
        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            print(f"Error: Cannot open source {self.source}")
            return

        # Determine delay between frames
        if isinstance(self.source, int):
            delay = 0  # camera, no delay
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = 1.0 / fps if fps > 0 else 0.03  # video playback
            time.sleep(delay)

        while self.thread_active:
            ret, frame = cap.read()
            if not ret:
                break  # end of video

            # Process frame
            result = self.process_frame(frame)

            # Convert to QImage
            rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_data.emit(qimg)

            # Wait to match video FPS
            if delay > 0:
                time.sleep(delay)

        cap.release()

    def process_frame(self, frame):
        """Detect green crabs and annotate frame"""
        result = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Green color range
        lower_green = np.array([25, 30, 20])
        upper_green = np.array([95, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Morphology
        kernel_small = np.ones((5,5), np.uint8)
        kernel_large = np.ones((7,7), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_large, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_small, iterations=2)

        # Contours
        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 500
        max_area = 50000
        valid_crabs = [c for c in contours if min_area < cv2.contourArea(c) < max_area]

        # Draw bounding boxes
        for i, c in enumerate(valid_crabs, 1):
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result, f'Crab {i}', (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.drawContours(result, [c], -1, (255, 0, 0), 2)

        cv2.putText(result, f'Count: {len(valid_crabs)}', (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        return result

    def stop(self):
        self.thread_active = False
        self.quit()
        self.wait()
