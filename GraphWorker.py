# graph_worker.py
import time
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

class GraphWorker(QThread):

    # Send graph data to UI
    graph_data_ready = pyqtSignal(dict)

    def __init__(self, update_interval_ms=1000):
        super().__init__()
        self.index = 0
        self.x_data = []
        self.y_data = []

        self.timer = None

        # For FPS calculation
        self.last_time = time.time()
        self.update_interval_ms = update_interval_ms

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_graph_data)
        self.timer.start(self.update_interval_ms)
        self.exec_()

    def generate_graph_data(self):
        # ========== FPS calculation ==========
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        fps = 1.0 / dt if dt > 0 else 0

        # ========== Store FPS as Y VALUE ==========
        self.x_data.append(self.index)
        self.y_data.append(fps)
        self.index += 1

        # Keep last 20 points
        if len(self.x_data) > 20:
            self.x_data = self.x_data[-20:]
            self.y_data = self.y_data[-20:]

        # ========== Package for UI ==========
        graph_payload = {
            "x": self.x_data,
            "y": self.y_data,
            "title": "Graph FPS Over Time",
            "xlabel": "Frame",
            "ylabel": "FPS",

            "style": {
                "marker": "o",
                "line_color": "#4CAF50",
                "line_width": 2,
                "background": "#071e26",
                "grid_alpha": 0.3,
                "text_color": "#d6e8ea",
                "spine_color": "#1a343d",
            }
        }

        self.graph_data_ready.emit(graph_payload)

    def stop(self):
        if self.timer:
            self.timer.stop()
        self.quit()
        self.wait()
