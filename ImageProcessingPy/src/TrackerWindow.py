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

        self.box2 = QtGui.QWidget()
        bBGR = QtGui.QPushButton("BGR", self.box2)
        bBGR.clicked.connect(lambda:self.outputConfig(bBGR))
        
        bHSV = QtGui.QPushButton("HSV", self.box2)
        bHSV.clicked.connect(lambda:self.outputConfig(bHSV))
        
        bNone = QtGui.QPushButton("None", self.box2)
        bNone.clicked.connect(lambda:self.outputConfig(bNone))
        
        debugCheckbox = QtGui.QCheckBox("Debug")
        debugCheckbox.setChecked(imgProcessor.getDebug())
        debugCheckbox.clicked.connect(lambda:self.changeDebugMode(debugCheckbox))
        
        hbox = QtGui.QGridLayout(self.box2)
        hbox.addWidget(bBGR,0,0)
        hbox.addWidget(bHSV,0,1)
        hbox.addWidget(bNone,0,2)
        hbox.addWidget(debugCheckbox,1,1)
        self.box2.setLayout(hbox)
        self.box2.setEnabled(False)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.box2)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)

        self.setLayout(vbox)
        self.setGeometry(100,100,200,200)
        self.show()
        
    def startCapture(self):        
        print "startCapture"
        self.start_button.setEnabled(False)
        self.end_button.setEnabled(True)
        self.box2.setEnabled(True)
        self.imageProcessor.processImage()
        
    def outputConfig(self, b):
        self.imageProcessor.setOutputMode(b.text())
        
    def endCapture(self):
        print "endCapture"
        self.end_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.box2.setEnabled(False)
        self.imageProcessor.endImageProcessing()
        
    def quitCapture(self):
        print "quitCapture"
        self.imageProcessor.quitImageProcessing()
        QtCore.QCoreApplication.quit()
        
    def changeDebugMode(self, cb):
        self.imageProcessor.setDebug(cb.isChecked())
        
        