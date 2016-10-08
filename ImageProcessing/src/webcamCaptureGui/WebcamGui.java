package webcamCaptureGui;

import java.awt.Dimension;
import java.awt.GridBagLayout;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
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
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.objdetect.CascadeClassifier;


public class WebcamGui extends JFrame implements WindowListener {

	private static final long serialVersionUID = 3732418556012706424L;
	private static final int WEBCAM_PX_WIDTH = 640;
	private static final int WEBCAM_PX_HEIGHT =  480;

	private JLabel videoFrame;
	private Thread webcam;
	
	public WebcamGui() {
		setTitle("Webcam");
		setSize(new Dimension(WEBCAM_PX_WIDTH+16, WEBCAM_PX_HEIGHT+39));
		
		addWindowListener(this);
		
		setLayout(new GridBagLayout());

		videoFrame = new JLabel();
		videoFrame.setSize(WEBCAM_PX_WIDTH, WEBCAM_PX_HEIGHT);
		add(videoFrame);
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		setVisible(true);
	}

	public void webcamCapture() {
		webcam = new Thread() {
			public void run() {
				VideoCapture capture = new VideoCapture(0);
				capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
				capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
				
				//capture.open(0);

				Mat image = new Mat();
				capture.read(image);
								
				while (true && isVisible()) {		
					if (capture.read(image)) {
						System.out.println("Sucessful");
						CascadeClassifier circleDetector = new CascadeClassifier("cascade.xml");

						MatOfRect detections = new MatOfRect();
						circleDetector.detectMultiScale(image, detections);
						
						for (Rect rect : detections.toArray()) {
							Imgproc.rectangle(image, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));
						}
						
						ImageIcon frame = new ImageIcon(bufferedImage(image));
						videoFrame.setIcon(frame);
					} else {
						System.out.println("Dropped Frame");
					}
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

		WebcamGui gui = new WebcamGui();
		gui.webcamCapture();
	}

	@Override
	public void windowActivated(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowClosed(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowClosing(WindowEvent arg0) {
		setVisible(false);
		
		while(webcam.isAlive()) {
			// Wait for webcam thread to terminate before closing main thread
		}
	
		System.out.println("Closing");
	}

	@Override
	public void windowDeactivated(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowDeiconified(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowIconified(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowOpened(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

}
