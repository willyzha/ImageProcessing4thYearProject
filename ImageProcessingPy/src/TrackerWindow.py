import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

class Window(QtGui.QWidget):
    def __init__(self, imgProcessor):

        self.imageProcessor = imgProcessor

        QtGui.QWidget.__init__(self)
        self.setWindowTitle('Control Panel')

        # self.capture = Capture()
        self.start_button = QtGui.QPushButton('Start',self)
        self.start_button.setEnabled(True)
        self.start_button.clicked.connect(self.startCapture)
        
        self.end_button = QtGui.QPushButton('End',self)
        self.end_button.clicked.connect(self.endCapture)
        self.end_button.setEnabled(False)
        
        self.quit_button = QtGui.QPushButton('Quit',self)
        self.quit_button.setEnabled(True)
        self.quit_button.clicked.connect(self.quitCapture)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)

        self.setLayout(vbox)
        self.setGeometry(100,100,200,200)
        self.show()
        
    def startCapture(self):        
        print "startCapture"
        self.start_button.setEnabled(False)
        self.end_button.setEnabled(True)
        self.imageProcessor.processImage()
        
    def endCapture(self):
        print "endCapture"
        self.end_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.imageProcessor.endImageProcessing()
        
    def quitCapture(self):
        print "quitCapture"
        self.imageProcessor.quitImageProcessing()
        QtCore.QCoreApplication.quit()
        