import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from Threads.CameraDisplay import CameraWorker
from Threads.GraphWorker import GraphWorker
from Threads.Tableworker import TableWorker
from Threads.ObjectDetectionWorker import ObjectDetectionWorker


# Matplotlib canvas for graph
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi(r"D:\ROV\Session 10\integration\designfirst.ui", self)

        # ======================================================
        # Graph setup
        # ======================================================
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.graph_layout.addWidget(self.canvas)

        self.graph_worker = GraphWorker()
        self.graph_worker.graph_data_ready.connect(self.update_graph)
        self.graph_worker.start()

        # ======================================================
        # Camera setup (3 cameras)
        # ======================================================
        self.camera_workers = []
        self.camera_labels = [self.MainCamera, self.Camera2, self.Camera3]
        # Use only one CameraWorker for the real camera
        worker = CameraWorker(camera_index=0)
        # Send the same frame to all 3 labels
        worker.image_data.connect(lambda qimg: [self.update_camera_display(idx, qimg) for idx in range(3)])
        worker.file_saved.connect(self.add_file_to_list)
        worker.start()
        self.camera_workers.append(worker)
        # for i in range(3):
        #     worker = CameraWorker(camera_index=0)
        #     worker.image_data.connect(lambda qimg, idx=0: self.update_camera_display(idx, qimg))
        #     worker.file_saved.connect(self.add_file_to_list)
        #     worker.start()
        #     self.camera_workers.append(worker)

        self.freezeBtn.clicked.connect(self.freeze_camera)
        self.captureBtn.clicked.connect(self.capture_frame)
        self.recordBtn.clicked.connect(self.toggle_recording)

        # ======================================================
        # Table setup
        # ======================================================
        self.table_worker = TableWorker()
        self.table_worker.data_ready.connect(self.update_table)
        self.table_worker.start()

        # File system
        self.load_existing_files()
        self.fileListWidget.itemDoubleClicked.connect(self.open_file)
        self.od_worker = None
        self.odStartBtn.clicked.connect(self.start_od_detection)
        self.load_od_files()

    # ============================================================
    # Camera
    # ============================================================

    def update_camera_display(self, idx, qimg):
        """Update camera display for a specific camera."""
        label = self.camera_labels[idx]
        label.setPixmap(QPixmap.fromImage(qimg))

    def freeze_camera(self):
        cam = self.camera_workers[0]
        cam.toggle_freeze()
        self.freezeBtn.setText("Unfreeze" if cam.is_frozen else "Freeze")

    def capture_frame(self):
        self.camera_workers[0].capture_frame()

    def toggle_recording(self):
        cam = self.camera_workers[0]
        filepath = cam.toggle_recording()

        if cam.is_recording:
            self.recordBtn.setText("Stop Recording")
            self.recordBtn.setStyleSheet("background-color: #c62828;")
            if filepath:
                self.add_file_to_list(filepath)
        else:
            self.recordBtn.setText("Start Recording")
            self.recordBtn.setStyleSheet("")

    # ============================================================
    # Graph
    # ============================================================

    def update_graph(self, data):
        """Draw graph using worker-processed FPS data."""
        style = data["style"]

        self.canvas.ax.clear()

        # Plot FPS
        self.canvas.ax.plot(
            data["x"],
            data["y"],
            marker=style["marker"],
            color=style["line_color"],
            linewidth=style["line_width"]
        )

        # Labels
        self.canvas.ax.set_title(data["title"])
        self.canvas.ax.set_xlabel(data["xlabel"])
        self.canvas.ax.set_ylabel(data["ylabel"])

        # Theme (sent from worker)
        self.canvas.ax.set_facecolor(style["background"])
        self.canvas.fig.patch.set_facecolor(style["background"])
        self.canvas.ax.grid(True, alpha=style["grid_alpha"])
        self.canvas.ax.tick_params(colors=style["text_color"])
        self.canvas.ax.xaxis.label.set_color(style["text_color"])
        self.canvas.ax.yaxis.label.set_color(style["text_color"])
        self.canvas.ax.title.set_color(style["text_color"])

        # Border colors
        for spine in self.canvas.ax.spines.values():
            spine.set_color(style["spine_color"])

        self.canvas.draw()

    # ============================================================
    # Table
    # ============================================================

    def update_table(self, sensor_data):
        """Update 3x3 table with sensor data"""
        self.tableWidget.setRowCount(len(sensor_data))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Depth (m)", "Temperature (°C)", "Battery (%)"])

        for row_index, row_data in enumerate(sensor_data):
            for col_index, value in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value)))
    # ============================================================
    # File Handling
    # ============================================================
    def load_existing_files(self):
        """Load all existing captured images and videos"""
        self.fileListWidget.clear()
        
        # Load images
        image_folder = "captured_images"
        if os.path.exists(image_folder): 
            for filename in sorted(os.listdir(image_folder), reverse=True):
                if filename.endswith(('.jpg', '.png', '.jpeg')):
                    filepath = os.path.join(image_folder, filename)
                    item = QListWidgetItem(f"📷 {filename}")
                    item.setData(256, filepath)  # Store full path
                    self.fileListWidget.addItem(item)
        
        # Load videos
        video_folder = "recorded_videos"
        if os.path.exists(video_folder):
            for filename in sorted(os.listdir(video_folder), reverse=True):
                if filename.endswith(('.avi', '.mp4', '.mov')):
                    filepath = os.path.join(video_folder, filename)
                    item = QListWidgetItem(f"🎥 {filename}")
                    item.setData(256, filepath)  # Store full path
                    self.fileListWidget.addItem(item)
    
    def add_file_to_list(self, filepath):
        """Add newly saved file to the list"""
        filename = os.path.basename(filepath)
        
        # Determine icon based on file type
        if filename.endswith(('.jpg', '.png', '.jpeg')):
            icon = "📷"
        else:
            icon = "🎥"
        
        item = QListWidgetItem(f"{icon} {filename}")
        item.setData(256, filepath)  # Store full path
        self.fileListWidget.insertItem(0, item)  # Add at top
        # Add to Object Detection list
        od_item = QListWidgetItem(f"{icon} {filename}")
        od_item.setData(256, filepath)
        self.odFileListWidget.insertItem(0, od_item)
    
    def open_file(self, item):
        """Open file when double-clicked"""
        filepath = item.data(256)
        if os.path.exists(filepath):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(filepath)))
# Keep a reference to the worker so it doesn't get garbage collected
    

# In MainWindow class

    def load_od_files(self):
        """Load video/image files into Object Detection tab list"""
        self.odFileListWidget.clear()
        folders = ["recorded_videos", "captured_images"]
        for folder in folders:
            if os.path.exists(folder):
                for filename in sorted(os.listdir(folder), reverse=True):
                    filepath = os.path.join(folder, filename)
                    if folder == "recorded_videos" and filename.lower().endswith(('.mp4','.avi','.mov')):
                        item = QListWidgetItem(f"🎥 {filename}")
                        item.setData(256, filepath)
                        self.odFileListWidget.addItem(item)
                    elif folder == "captured_images" and filename.lower().endswith(('.jpg','.png','.jpeg')):
                        item = QListWidgetItem(f"📷 {filename}")
                        item.setData(256, filepath)
                        self.odFileListWidget.addItem(item)

    def start_od_detection(self):
        """Start object detection on selected file"""
        selected_items = self.odFileListWidget.selectedItems()
        if not selected_items:
            return

        filepath = selected_items[0].data(256)

        # Stop previous worker if running
        if self.od_worker is not None:
            self.od_worker.stop()
            self.od_worker = None

        # Start new worker
        self.od_worker = ObjectDetectionWorker(filepath)
        self.od_worker.image_data.connect(
            lambda qimg: self.odDisplayLabel.setPixmap(QPixmap.fromImage(qimg))
        )
        self.od_worker.start()




    # ============================================================
    # Close Event
    # ============================================================

    def closeEvent(self, event):
        # Stop all cameras
        for worker in self.camera_workers:
            worker.stop()

        # Stop graph + table workers
        self.graph_worker.stop()
        self.table_worker.stop()

        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())