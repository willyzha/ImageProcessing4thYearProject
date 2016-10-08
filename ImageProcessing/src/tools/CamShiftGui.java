package tools;

import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.util.ArrayList;
import java.util.List;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JTextField;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfFloat;
import org.opencv.core.MatOfInt;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;
import org.opencv.core.Scalar;
import org.opencv.core.TermCriteria;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.CascadeClassifier;
import org.opencv.video.Video;

public class CamShiftGui extends JFrame implements WindowListener, ActionListener{

	private static final long serialVersionUID = 5377770257924553424L;
	private static final int WEBCAM_PX_WIDTH = 640;
	private static final int WEBCAM_PX_HEIGHT =  480;
	
	private Thread webcam;
	/**
	 *  GUI ELEMENTS
	 */
	private JLabel videoIcon;
	private JButton startButton;
	private JTextField xTextField;
	private JTextField yTextField;
	private JTextField widthTextField;
	private JTextField heightTextField;
	private boolean tracking;
	private Mat image = new Mat();
	
    MatOfInt channels = new MatOfInt(0);
    MatOfFloat ranges = new MatOfFloat(0f, 180f);
	
	Mat roi_hist;
	public CamShiftGui() {
		tracking = false;
		roi_hist = null;
		
		addWindowListener(this);
		
		setTitle("Camshift");
		setLayout(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();
		
		videoIcon = new JLabel();
		videoIcon.setPreferredSize(new Dimension(WEBCAM_PX_WIDTH, WEBCAM_PX_HEIGHT));
		
		c.fill = GridBagConstraints.HORIZONTAL;
		c.gridx = 0;
		c.gridy = 0;
		c.gridwidth = 4;
		add(videoIcon, c);
		
		xTextField = new JTextField();
		xTextField.setText("x");
		xTextField.addActionListener(this);
		yTextField = new JTextField();
		yTextField.setText("y");
		yTextField.addActionListener(this);
		widthTextField = new JTextField();
		widthTextField.setText("width");
		widthTextField.addActionListener(this);
		heightTextField = new JTextField();
		heightTextField.setText("height");
		heightTextField.addActionListener(this);
		
		c.gridwidth = 1;
		c.gridy = 1;
		c.gridx = 0;
		c.weightx = 0.25;
		add(xTextField, c);
		c.gridx = 1;
		add(yTextField, c);
		c.gridx = 2;
		add(widthTextField, c);
		c.gridx = 3;
		add(heightTextField, c);
		
		startButton = new JButton("Start");
		startButton.setActionCommand("StartTracking");
		startButton.addActionListener(this);
		c.gridwidth = 4;
		c.gridy = 2;
		c.gridx = 0;
		c.weightx = 1;
		add(startButton, c);
		
		pack();
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		setVisible(true);
	}
	
	public void webcamCapture() {
		webcam = new Thread() {
			public void run() {				
				VideoCapture capture = new VideoCapture(0);

				capture.open(0);
				capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
				capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
								
				TermCriteria criteria = new TermCriteria(TermCriteria.COUNT + TermCriteria.EPS, 10, 1);
				
				while (true && isVisible()) {
					int frameCount = 0;
					if (frameCount > 30) {
						try {
							Thread.sleep(1000);
						} catch (InterruptedException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					} else if (capture.read(image) && roi_hist != null) {
						Mat hsv = new Mat();
						Mat dst = new Mat();
						
						Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
						List<Mat> hsv_list = new ArrayList<Mat>();
						hsv_list.add(hsv);
						Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
						
						Rect trackWindow = new Rect(240, 30, 140, 140);
						
						RotatedRect newWindow = Video.CamShift(dst, trackWindow, criteria);
						
						Mat markedupImage = image.clone();	
						
						Imgproc.rectangle(markedupImage, 
								new Point(newWindow.boundingRect().x, newWindow.boundingRect().y), 
								new Point(newWindow.boundingRect().x + newWindow.boundingRect().width, 
										newWindow.boundingRect().y + newWindow.boundingRect().height),
								new Scalar(0, 255, 0));
						
						ImageIcon frame = new ImageIcon(bufferedImage(markedupImage));
						videoIcon.setIcon(frame);
					} else if (capture.read(image)) {
						ImageIcon frame = new ImageIcon(bufferedImage(image));
						videoIcon.setIcon(frame);
					} else {
						System.out.println("Dropped Frame");
					}
				}
				capture.release();
			}
		};
		
		webcam.start();
	}
	
	public static void main(String args[]) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);

		CamShiftGui gui = new CamShiftGui();
		gui.webcamCapture();
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
	
	@Override
	public void actionPerformed(ActionEvent e) {
		if (e.getActionCommand().equals("StartTracking")) {
			tracking = true;
			
			System.out.println("Tracking = " + tracking);
		    
			if (!image.empty()) {
				Mat hsvImg_ROI = new Mat();
				Mat roi = image.submat(new Rect(240, 30, 140, 140));
				Imgproc.cvtColor(roi, hsvImg_ROI, Imgproc.COLOR_BGR2HSV);
				
				Scalar lowerb = new Scalar(0, 60, 32);
				Scalar upperb = new Scalar(180, 255, 255);
				
				Mat mask = new Mat();
				Core.inRange(hsvImg_ROI, lowerb, upperb, mask);

			    MatOfInt histSize = new MatOfInt(180);		    

			    List<Mat> hsvImg_ROI_List = new ArrayList<Mat>();
			    roi_hist = new Mat();
			    hsvImg_ROI_List.add(hsvImg_ROI);
				Imgproc.calcHist(hsvImg_ROI_List, channels, mask, roi_hist, histSize, ranges);
				
				Core.normalize(roi_hist, roi_hist, 0, 255, Core.NORM_MINMAX);
			}
		}
	}

	@Override
	public void windowActivated(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowClosed(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowClosing(WindowEvent e) {
		setVisible(false);
		
		while(webcam.isAlive()) {
			// Wait for webcam thread to terminate before closing main thread
		}

		System.out.println("Closing");
	}

	@Override
	public void windowDeactivated(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowDeiconified(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowIconified(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public void windowOpened(WindowEvent e) {
		// TODO Auto-generated method stub
		
	}
}
