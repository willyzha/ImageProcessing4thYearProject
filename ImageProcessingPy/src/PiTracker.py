import argparse
import ImageProcessing
from ImageProcessing import enableDebug
from ImageProcessing import ImageProcessor
from PiCamModule import PiCam
import PySide.QtGui as QtGui
from TrackerGui import Window

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform Camshift Tracking.\nUsage: \t"i" to select ROI\n\t"q" to exit' , formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument('-d','--debug', dest='debug', action='store_const', const=True, default=False, help='enable debug mode. Displays multiple screens and saves .jpg images.')
    parser.add_argument('-filter', dest='avgFilterN', default=10, type=int, help='set length of averaging filter.')
    parser.add_argument('-resolution', dest='res', default=[640, 480], nargs=2, type=int, help='set resolution of camera video capture. usage: -resolution [X] [Y].')
    args = parser.parse_args()

    debug = args.debug
    avgFilterN = args.avgFilterN
    resolution = args.res
    
    if debug:
        enableDebug()        
    
    import sys
    app = QtGui.QApplication(sys.argv)
        
    camera = PiCam(resolution)    
    processer = ImageProcessor(camera, resolution, avgFilterN)
    window = Window(processer)
    sys.exit(app.exec_())