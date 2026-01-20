from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import cv2
import os
import sys

from camera import cameraW
from graph import graphW
from timer import timerW
from table import tableW

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi("designer (1).ui", self)        
        # self.mainDisplay.setText("hello")
        self.mainWorker = cameraW(0,self.listWidget,self.screenshot,self.record,self.objectdetect,self.Object_Label)
        self.gworker = graphW(self.graph)
        self.tableWorker = tableW(self.Table_2,self.calc)
        self.mainWorker.img.connect(lambda img: self.x(img))
        self.timerworker = timerW(self.taskLabel,self.missionLabel,self.startButton,self.resetButton)

        self.mainWorker.start()
        self.gworker.start()
        self.timerworker.start()
        self.tableWorker.start()
    
    def x(self,img):
        self.mainDisplay.setPixmap(QtGui.QPixmap.fromImage(img))
        self.camLeft.setPixmap(QtGui.QPixmap.fromImage(img))
        self.camRight.setPixmap(QtGui.QPixmap.fromImage(img))
        self.camDown.setPixmap(QtGui.QPixmap.fromImage(img))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = mainWindow()
    MainWindow.show()
    
    # Ensure proper cleanup on exit
    result = app.exec_()
        
    sys.exit(result)