import random
from PyQt5.QtCore import QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import time

class canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.figur = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.figur.add_subplot(111)
        super().__init__(self.figur)

class graphW(QThread):

    def __init__(self,graph):
        super().__init__()
        self.active = True
        self.xl = []
        self.yl = []
        self.index = 1
        self.graph = graph

        self.canva = canvas()
        self.graph.addWidget(self.canva)

    def run(self):
        while self.active:
            self.xl.append(self.index)
            self.yl.append(random.randint(1,100))
            self.index += 1

            if len(self.xl) > 20:
                self.xl = self.xl[-20:]
                self.yl = self.yl[-20:]

            self.canva.ax.clear()
            self.canva.ax.plot(self.xl,self.yl,marker='o',color='r')
            self.canva.ax.set_xlabel("x")
            self.canva.ax.set_ylabel("y")
            self.canva.ax.set_title("title")
            self.canva.draw()

            time.sleep(1)

    def stop(self):
        self.active = False
        self.quit()