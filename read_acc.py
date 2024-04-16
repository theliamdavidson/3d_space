import serial
import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from time import sleep

class DeviceCommunicationThread(QThread):
    measurements_updated = pyqtSignal(dict)
    def __init__(self, ):
        super().__init__()

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
        self.communication_thread = DeviceCommunicationThread()
        self.communication_thread.measurements_updated.connect(self.updateData)
        self.communication_thread.start()
        self.measurements = {"x" : None,
                             "y" : None,
                             "z" : None}
        self.lock = True
        self.valueSaved = False
    def keyPressEvent(self, event):
       if event.key() == Qt.Key_Space:
           self.freezeCalled()

    def initUI(self):
        self.setWindowTitle("IMU Readings")
        self.setGeometry(10,30,1890,1080)
        layout = QVBoxLayout(self)
        rawDataHorizontal = QHBoxLayout(self)
        savedDataHorizontal = QHBoxLayout(self)
        self.rawValueLabels= {}
        self.savedValueLabels = {}
        measurementLabels = [
            "x", "y", "z"           
        ]
        
        for measurement in measurementLabels:
            value_label = QLabel("Connecting...", alignment=Qt.AlignCenter)    # if "Connecting" remains for more than 10 seconds, something is wrong with the connection
            value_label.setFont(QFont('Arial', 20))
            rawDataHorizontal.addWidget(value_label)
            self.rawValueLabels[measurement] = value_label
        layout.addLayout(rawDataHorizontal)

        for label in measurementLabels:
            savedValueLabel = QLabel("", alignment=Qt.AlignCenter)    
            savedValueLabel.setFont(QFont('Arial', 20))
            savedDataHorizontal.addWidget(savedValueLabel)
            self.savedValueLabels[label] = savedValueLabel
        layout.addLayout(savedDataHorizontal)
        
        freeze = QPushButton(f'Freeze', self)
        freeze.clicked.connect(self.freezeCalled)
        layout.addWidget(freeze)

        self.setLayout(layout)
        self.show()
    
    def updateData(self, values):
        while self.lock == False:
            sleep(.1)
            print("wait")

        self.lock = False
        for label, labelIndex in self.rawValueLabels.items():
            value = values[label]
            labelIndex.setText(f'{label}: {value}')
            self.measurements[label] = value
        if self.valueSaved == True:
            self.checkMatching()
        self.lock = True

    def checkMatching(self):
        pass
    def freezeCalled(self):
        while self.lock == False:
            sleep(.1)
            print("wait")

        self.lock = False
        self.valueSaved = True
        for label, labelIndex in self.savedValueLabels.items():
            value = self.measurements[label] 
            labelIndex.setText(f'{label}: {value}')
            print(label, value)
        self.lock = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = viewWindow()
    sys.exit(app.exec_())