from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QListWidget, QListWidgetItem
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import cv2
import os
import sys
from datetime import datetime
from object import objectW

class cameraW(QThread):
    img = pyqtSignal(QtGui.QImage)
    def __init__(self,index,fileList,scbutton,vButton,dButton,detectLabel):
        super().__init__()
        self.active = True
        self.index = index
        self.fileList = fileList
        self.screenshotButton = scbutton
        self.scIndex = 1
        self.recording = False
        self.video = None
        self.vIndex = 1
        self.recordButton = vButton
        self.detectButton = dButton
        self.detectLabel = detectLabel
        self.odW =None

        self.folder_path = "files"
        os.makedirs(self.folder_path,exist_ok=True)

        self.load_exisiting_files()
        self.fileList.itemDoubleClicked.connect(self.open_file)

        self.screenshotButton.clicked.connect(self.screenShot)
        self.recordButton.clicked.connect(self.record)
        self.detectButton.clicked.connect(self.objectdetect)

    def run(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            print("Camera could not be opened")
            return
            
        while self.active:
            ret, self.frame = self.cap.read()

            if not ret:
                print("Failed to grab frame")
                continue

            if self.recording and self.video is not None:
                self.video.write(self.frame)

            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w

            qimage = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

            self.img.emit(qimage)

    def load_exisiting_files(self):
        self.fileList.clear()

        if os.path.exists(self.folder_path):
            for filename in sorted(os.listdir(self.folder_path)):
                if filename.endswith(('.jpg', '.png', '.jpeg')):
                    filepath = os.path.join(self.folder_path, filename)
                    item = QListWidgetItem(f"(photo) {filename}")
                    item.setData(256, filepath)
                    self.fileList.addItem(item)
                else:
                    if filename.endswith(('.mp4', '.avi', '.mov')):
                        filepath = os.path.join(self.folder_path, filename)
                        item = QListWidgetItem(f"(video) {filename}")
                        item.setData(256, filepath)
                        self.fileList.addItem(item)

    def open_file(self,item):
        filepath = item.data(256)
        if os.path.exists(filepath):
            QtGui.QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

    def screenShot(self):
        format_string = "%Y_%m_%d_%H_%M_%S"
        timestamp = datetime.now().strftime(format_string)
        filename = f'{self.scIndex}_{timestamp}.png'
        print(filename)
        filepath = os.path.join(self.folder_path, filename)
        cv2.imwrite(filepath,self.frame)
        self.load_exisiting_files()
        self.scIndex += 1
    
    def record(self):
        self.recording = not self.recording
        if self.recording:
            self.recordButton.setText('Stop recording')
            self.recordButton.setStyleSheet('QPushButton {background-color: red}')
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = 30.0

            format_string = "%Y_%m_%d_%H_%M_%S"
            timestamp = datetime.now().strftime(format_string)
            filename = f'{self.vIndex}_{timestamp}.mp4'
            filepath = os.path.join(self.folder_path, filename)
            self.video = cv2.VideoWriter(filepath,fourcc,fps,(frame_width, frame_height))
        else:
            self.recordButton.setText('Record')
            self.recordButton.setStyleSheet('')
            self.vIndex += 1
            self.video.release()
            self.load_exisiting_files()

    def objectdetect(self):
        item = self.fileList.selectedItems()
        if not item:
            return
        
        filepath = item[0].data(256)

        if self.odW is not None:
            self.odW.stop()
            self.odW = None

        self.odW = objectW(filepath,self.detectLabel)
        self.odW.start()

    def stop(self):
        self.active = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.quit()