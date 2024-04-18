import serial
import sys
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont
import logging

class DeviceCommunicationThread(QThread):
    measurements_updated = pyqtSignal(dict)
    def __init__(self, ):
        super().__init__()
        self.comPort = 'COM5'

    def run(self):
        with serial.Serial(self.comPort, 9600, timeout=1) as ser:
            while not self.isInterruptionRequested():
                received_values = {"x" : None,
                                   "y" : None,
                                   "z" : None}
                self.cleanEmit(ser, received_values)

    def cleanEmit(self, ser, received_values):
        count = 0
        while count < 3:
            response = ser.readline().decode().strip()
            values = response.split(':')
            if values[0] in received_values:
                received_values[values[0]] = values[1]
                count += 1     
            else:
                logging.info(response)
            logging.debug('emit')
        self.measurements_updated.emit(received_values)

            
class ViewWindow(QWidget):
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

    def keyPressEvent(self, event):
       if event.key() == Qt.Key_Space:
           self.freezeCalled()

    def initUI(self):
        self.setWindowTitle("IMU Readings")
        #self.setGeometry(10,30,1890,1080)
        layout = QVBoxLayout(self)
        rawDataHorizontal = QHBoxLayout(self)
        savedDataHorizontal = QHBoxLayout(self)
        progressBarHorizontal = QHBoxLayout(self)
        self.rawValueLabels = {}
        self.savedValueLabels = {}
        self.progressBars = {}
        measurementLabels = [
            "x", "y", "z"           
        ]
        
        for measurement in measurementLabels:
            value_label = QLabel("Connecting...", alignment=Qt.AlignCenter)    # if "Connecting" remains for more than 10 seconds, something is wrong with the connection
            savedValueLabel = QLabel("", alignment=Qt.AlignCenter)
            visualAid = QProgressBar(alignment=Qt.AlignCenter)
            visualAid.setValue(0)

            value_label.setFont(QFont('Arial', 20))
            savedValueLabel.setFont(QFont('Arial', 20))
            visualAid.setRange(0, 100)

            rawDataHorizontal.addWidget(value_label)
            savedDataHorizontal.addWidget(savedValueLabel)
            progressBarHorizontal.addWidget(visualAid)

            self.rawValueLabels[measurement] = value_label
            self.savedValueLabels[measurement] = savedValueLabel
            self.progressBars[measurement] = visualAid

        layout.addLayout(rawDataHorizontal)            
        layout.addLayout(savedDataHorizontal)
        layout.addLayout(progressBarHorizontal)
        
        freeze = QPushButton(f'Freeze', self)
        freeze.clicked.connect(self.freezeCalled)
        layout.addWidget(freeze)

        self.setLayout(layout)
        self.show()
    
    def updateData(self, values):
        #while self.lock == False:
        #    sleep(.1)
        #    print("wait")

        #self.lock = False
        logging.debug('update')
        for label, labelIndex in self.rawValueLabels.items():
            value = values[label]
            labelIndex.setText(f'{label}: {value}')
            self.measurements[label] = value
            saved_value = self.savedValueLabels[label].text()
            if saved_value:
                saved_value = int(saved_value.split(": ")[1]) + 10          # since the range is (-10 - 10)
                difference = abs(saved_value - (int(value)+ 10))            # adding 10 makes the cases easier to follow
                if saved_value != 0:
                    progress = int((1 - difference / abs(saved_value)) * 100)
                else:
                    progress = 100 if value == 0 else 0
                self.progressBars[label].setValue(progress)
        #self.lock = True


    def freezeCalled(self):
        #while self.lock == False:
        #    sleep(.1)
        #    print("wait")

        #self.lock = False
        logging.debug('frozen')
        for label, labelIndex in self.savedValueLabels.items():
            value = self.measurements[label] 
            labelIndex.setText(f'{label}: {value}')
            logging.debug(label, value)
        #self.lock = True

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    app = QApplication(sys.argv)
    window = ViewWindow()
    sys.exit(app.exec_())