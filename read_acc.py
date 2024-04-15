import serial
import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from queue import Queue

class DeviceCommunicationThread(QThread):
    measurements_updated = pyqtSignal(dict)
    def __init__(self, queue):
        super().__init__()
        self.data_queue = queue

    def run(self):
        with serial.Serial('COM5', 9600, timeout=1) as ser:
            while not self.isInterruptionRequested():
                received_values = {"x" : None,
                                   "y" : None,
                                   "z" : None}
                count = 0
                while count < 3:
                    response = ser.readline().decode().strip()
                    values = response.split(':')
                    if values[0] in received_values:
                        received_values[values[0]] = values[1]
                        count += 1                    
                self.measurements_updated.emit(received_values)
                

class viewWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # Create the communication thread
        telemetry_queue = Queue()        
        self.communication_thread = DeviceCommunicationThread(telemetry_queue)
        self.communication_thread.measurements_updated.connect(self.updateData)
        self.communication_thread.start()

    def initUI(self):
        self.setWindowTitle("IMU Readings")
        self.setGeometry(10,30,1890,1080)
        layout = QHBoxLayout(self)
        self.value_labels= {}
        measurements = [
            "x", "y", "z"           
        ]
        for measurement in measurements:
            value_label = QLabel("Connecting...", alignment=Qt.AlignCenter)    # if you have time to read "Connecting", something is wrong with the connection
            value_label.setFont(QFont('Arial', 20))
            layout.addWidget(value_label)
            self.value_labels[measurement] = value_label
        self.setLayout(layout)
        self.show()
    
    def updateData(self, values):
        for label, labelIndex in self.value_labels.items():
            value = values[label]
            labelIndex.setText(f'{label}: {value}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = viewWindow()
    sys.exit(app.exec_())