import cv2
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

def startCapture(cap):
    print "pressed start"
    while(True):
        _, frame = cap.read()
        cv2.imshow("Capture", frame)
        cv2.waitKey(5)
    cv2.destroyAllWindows() 

def endCapture(cap):
    print "pressed End"
    cv2.destroyAllWindows()

def quitCapture(cap):
    print "pressed Quit"
    cv2.destroyAllWindows()
    cap.release()
    QtCore.QCoreApplication.quit()

class Window(QtGui.QWidget):
    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setWindowTitle('Control Panel')

        self.capture = Capture()
        self.start_button = QtGui.QPushButton('Start',self)
        self.start_button.clicked.connect(self.capture.startCapture)
        
        self.end_button = QtGui.QPushButton('End',self)
        self.end_button.clicked.connect(self.capture.endCapture)
        
        self.quit_button = QtGui.QPushButton('Quit',self)
        self.quit_button.clicked.connect(self.capture.quitCapture)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)

        self.setLayout(vbox)
        self.setGeometry(100,100,200,200)
        self.show()

class Capture():
    def __init__(self):
        self.capturing = False
        self.c = cv2.VideoCapture(0)

    def startCapture(self):
        print "pressed start"
        self.capturing = True
        cap = self.c
        while(self.capturing):
            _, frame = cap.read()
            cv2.imshow("Capture", frame)
            cv2.waitKey(5)
        cv2.destroyAllWindows()

    def endCapture(self):
        print "pressed End"
        self.capturing = False
        print "end capture"
        # cv2.destroyAllWindows()

    def quitCapture(self):
        print "pressed Quit"
        self.capturing = False
        cap = self.c
        cv2.destroyAllWindows()
        cap.release()
        QtCore.QCoreApplication.quit()

if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())