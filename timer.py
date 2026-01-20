from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import cv2
import os
import sys

class timerW(QThread):
    def __init__(self,taskLabel,missionLabel,startButton,resetButton):
        super().__init__()
        self.taskLabel = taskLabel
        self.missionLabel = missionLabel
        self.startButton = startButton
        self.resetButton = resetButton
        self.missionOn = False
        self.taskOn = False

        self.missionSeconds = 60 * 60
        self.taskSeconds = 15 * 60

        self.missionTimer = QTimer()
        self.taskTimer = QTimer()

        self.missionTimer.timeout.connect(self.missionTimerr)
        self.taskTimer.timeout.connect(self.taskTimerr)

    def run(self):
        self.startButton.clicked.connect(self.startTimer)
        self.resetButton.clicked.connect(self.reset)

    def startTimer(self):
        if not self.missionOn:
            self.missionOn = True
            self.missionTimerr()
            self.missionTimer.start(1000)
            self.missionTimerr()
        if not self.taskOn:
            self.taskOn = True
            self.taskTimerr()
            self.taskTimer.start(1000)
            self.taskTimerr()
            
    def missionTimerr(self):
        minn, secc = divmod(self.missionSeconds,60)
        self.missionLabel.setText(f"{minn:02d}:{secc:02d}")
        self.missionSeconds -= 1

    def taskTimerr(self):
        minn,secc = divmod(self.taskSeconds,60)
        self.taskLabel.setText(f"{minn:02d}:{secc:02d}")
        self.taskSeconds -= 1

    def reset(self):
        self.taskTimer.stop()
        self.taskOn = False
        self.taskSeconds = 15 * 60
        self.taskLabel.setText("15:00")