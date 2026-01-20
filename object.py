from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import time
import cv2
import os
import sys
import numpy as np

class objectW(QThread):
    def __init__(self, file,detectLabel):
        super().__init__()
        self.active = True
        self.file = file
        self.detectLabel = detectLabel
    
    def run(self):
        cap = cv2.VideoCapture(self.file)
        if not cap.isOpened():
            return
        
        if isinstance(self.file, int):
            delay = 0
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps > 0:
                delay = 1.0 / fps
            else:
                delay = 0.03
        #     time.sleep(delay)
        
        while self.active:
            ret, frame = cap.read()
            if not ret:
                break  

            result = self.detect(frame)

            rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w

            qimage = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.detectLabel.setPixmap(QtGui.QPixmap.fromImage(qimage))

            if delay > 0:
                time.sleep(delay)

        cap.release()

    def detect(self,frame):
        result = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_green = np.array([25, 30, 20])
        upper_green = np.array([95, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        kernel_small = np.ones((5,5), np.uint8)
        kernel_large = np.ones((7,7), np.uint8)
        mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_large, iterations=2)
        mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_small, iterations=2)

        contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = 500
        max_area = 50000
        valid_crabs = [c for c in contours if min_area < cv2.contourArea(c) < max_area]

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