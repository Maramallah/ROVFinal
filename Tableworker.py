# table_worker.py
import random
from PyQt5.QtCore import QThread, pyqtSignal
import time

class TableWorker(QThread):
    # Emit a ready-to-display table payload
    data_ready = pyqtSignal(list)  # Emit list of lists

    def __init__(self, update_ms=1000):
        super().__init__()
        self.update_interval = update_ms / 1000.0  # convert ms -> seconds
        self.running = True
        self.sensor_labels = ["Sensor 1", "Sensor 2", "Sensor 3"]

    def run(self):
        while self.running:
            readings = []
            for name in self.sensor_labels:
                depth = round(random.uniform(0, 100), 2)
                temp = round(random.uniform(10, 30), 1)
                battery = int(random.uniform(20, 100))
                readings.append([depth, temp, battery])  # emit as list
            self.data_ready.emit(readings)
            time.sleep(self.update_interval)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
