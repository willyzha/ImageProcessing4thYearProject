package webcamCaptureGui;

import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;

import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.highgui.Highgui;
import org.opencv.highgui.VideoCapture;
import org.opencv.objdetect.CascadeClassifier;


public class WebcamGui extends JFrame{

	private static final long serialVersionUID = 1L;
	private static final int WEBCAM_PX_WIDTH = 640;
	private static final int WEBCAM_PX_HEIGHT =  480;

	private JLabel videoFrame;
	
	public WebcamGui() {
		setTitle("Webcam");
		int width = 1280;
		int height = 720;
		setSize(new Dimension(width, height));
		setVisible(true);
		
		setLayout(new GridBagLayout());
		
		videoFrame = new JLabel();
		add(videoFrame);
	}

	public void webcamCapture() {
		Thread webcam = new Thread() {
			public void run() {
				VideoCapture capture = new VideoCapture(0);

				capture.open(0);
				capture.set(Highgui.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
				capture.set(Highgui.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
				
				Mat image = new Mat();
				capture.read(image);
				String filename = "webcamOut.png";
				Highgui.imwrite(filename, image);
								
				while (true && isVisible()) {			
					if (capture.read(image)) {
						System.out.println("Sucessful");

					}	  
			
					CascadeClassifier circleDetector = new CascadeClassifier("cascade.xml");

					MatOfRect detections = new MatOfRect();
					circleDetector.detectMultiScale(image, detections);
					
					for (Rect rect : detections.toArray()) {
						Core.rectangle(image, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));
					}
					
					ImageIcon frame = new ImageIcon(bufferedImage(image));
					System.out.println("START");

					videoFrame.setIcon(frame);
				    System.out.println("FINISH");

				}
				capture.release();
			}
		};
		
		webcam.start();
	}
	
	public static BufferedImage bufferedImage(Mat m) {
	    int type = BufferedImage.TYPE_BYTE_GRAY;
	    if ( m.channels() > 1 ) {
	        type = BufferedImage.TYPE_3BYTE_BGR;
	    }
	    BufferedImage image = new BufferedImage(m.cols(),m.rows(), type);
	    m.get(0,0,((DataBufferByte)image.getRaster().getDataBuffer()).getData()); // get all the pixels
	    return image;
	}
	
	public static void main(String[] args) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		// TODO Auto-generated method stub
		WebcamGui gui = new WebcamGui();
		gui.webcamCapture();
	}

}
