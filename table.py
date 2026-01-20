from PyQt5 import   QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QListWidgetItem, QVBoxLayout,QMessageBox
import random
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import time

class tableW(QThread):
    def __init__(self,table,button):
        super().__init__()
        self.tableWidget = table
        self.calculatebtn = button

        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["species", "count", "freq"])


    def run(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(5)
        for row in range(self.tableWidget.rowCount()):
            species_item= QTableWidgetItem()
            species_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row , 0 , species_item)
            
            count_item= QTableWidgetItem()
            count_item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(row , 1, count_item)
            
            freq_item= QTableWidgetItem("")
            freq_item.setTextAlignment(Qt.AlignCenter)
            freq_item.setFlags(freq_item.flags() & ~Qt.ItemIsEditable)
            self.tableWidget.setItem(row , 2 , freq_item)
            
            self.calculatebtn.clicked.connect(self.calculate_freq)
            
    def calculate_freq(self):
        total_count =0
        row_count =[]
        
        
        for row in  range(self.tableWidget.rowCount()):
            count_item= self.tableWidget.item(row,1)
            count_text =count_item.text() if count_item else "0"
            try:
                count= float(count_text)
                if count< 0:
                    raise ValueError
                
            except ValueError:
                count =0
                QMessageBox.warning(
                self.tableWidget,
                "Invalid input",
                f"Non-numeric value in row {row + 1}"
            )
                count_item.setText("0")
            row_count.append(count)
            total_count +=count
        for row, count in enumerate(row_count):
            freq_item = self.tableWidget.item(row,2)
            freq = 0 if total_count ==0 else (count / total_count)*100
            freq_item.setText(f"{freq:.2f}%")