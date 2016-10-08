package tools;

import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.objdetect.CascadeClassifier;

public class PhotoBooth extends JFrame implements ActionListener, WindowListener{
	/**
	 * serialVersionUID
	 */
	private static final long serialVersionUID = -7535672911057861331L;
	private JLabel videoFrame;
	private JButton snap;
	private JTextField fileName;
	VideoCapture capture = new VideoCapture(0);
	
	private int imgCounter;
	
	private static final int WEBCAM_PX_WIDTH = 640;
	private static final int WEBCAM_PX_HEIGHT =  480;
	private WebcamThread webcam;

	private class WebcamThread extends Thread {

		Mat image;
		
		public WebcamThread() {
			image = new Mat();
		}
		
		public Mat getImage() {
			return image;
		}
		
		public void run() {
			//capture.open(0);
			
			while (true && isVisible()) {				
				capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
				capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
				
				if (capture.read(image)) {
					CascadeClassifier detector = new CascadeClassifier("cascade.xml");

					MatOfRect detections = new MatOfRect();
					detector.detectMultiScale(image, detections);
					
					Mat markedupImage = image.clone();					
					for (Rect rect : detections.toArray()) {
						Imgproc.rectangle(markedupImage, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));
					}
					
					ImageIcon frame = new ImageIcon(bufferedImage(markedupImage));
					videoFrame.setIcon(frame);
					
				} else {
					System.out.println("NOT READY");
				}
				
			}
			capture.release();
		}
	}
	
	public PhotoBooth() {
		setTitle("PhotoBooth");
		imgCounter = 0;
		GridBagConstraints c = new GridBagConstraints();
		c.fill = GridBagConstraints.HORIZONTAL;
		
		setLayout(new GridBagLayout());
		setSize(new Dimension(WEBCAM_PX_WIDTH+16, WEBCAM_PX_HEIGHT+66));
		
		addWindowListener(this);
		
		videoFrame = new JLabel();
		videoFrame.setSize(WEBCAM_PX_WIDTH, WEBCAM_PX_HEIGHT);
		snap = new JButton("Take Photo!");
		fileName = new JTextField();
		fileName.setText(""+imgCounter);
		
		snap.addActionListener(this);
		c.weighty = 0.8;
		c.gridx = 0;
		c.gridy = 0;
		add(videoFrame, c);
		
		c.weighty = 0.2;
		c.gridx = 0;
		c.gridy = 1;
		c.weightx = 0.5;
		JPanel bottom = new JPanel();
		bottom.setLayout(new GridLayout(1, 2));
		
		bottom.add(snap);
		bottom.add(fileName);
		
		add(bottom, c);		
		webcam = new WebcamThread();
		
		setVisible(true);
		webcam.start();
		setDefaultCloseOperation(EXIT_ON_CLOSE); 
	}
	
	public void save() {

		String filename = "photoBooth\\webcamOut_"+imgCounter+".png";
		Imgcodecs.imwrite(filename, webcam.getImage());
		
		System.out.println("FINISH");

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
		new PhotoBooth();
	}
	
	@Override
	public void actionPerformed(ActionEvent e) {
		
		if (e.getSource() instanceof JButton) {
			imgCounter = Integer.parseInt(fileName.getText());
			save();
			fileName.setText((imgCounter+1)+"");
		}
	}

	@Override
	public void windowActivated(WindowEvent arg0) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowClosed(WindowEvent arg0) {
		capture.release();
		
		System.out.println("Closing");
		
	}

	@Override
	public void windowClosing(WindowEvent arg0) {
		setVisible(false);
		
		while(webcam.isAlive()) {
			// Wait for webcam thread to terminate before closing main thread
		}
			
		capture.release();
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
