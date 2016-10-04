package camShiftLib;

import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;

import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;
import org.opencv.core.Scalar;

public class CamShiftGui extends JFrame implements ActionListener, WebcamListener, WindowListener, DocumentListener, ConfigurationListener{

	private static final long serialVersionUID = 2028612532446093868L;
	
	private JLabel videoIcon;
	private JButton startButton;
	private JButton configureButton;
	private JLabel x;
	private JLabel y;
	private JLabel width;
	private JLabel height;
	private JTextField xTextField;
	private JTextField yTextField;
	private JTextField widthTextField;
	private JTextField heightTextField;
	private JComboBox<String> videoSelection;
	
	private ConfigurationGui configWindow;
	private Scalar lowerb;
	private Scalar upperb;
	
	private WebcamManager webcam;
	private Rect rectangle;
	
	private boolean camShiftAlgEnabled;
	private CamShiftAlg camShiftAlg;
	private Mat lastFrameReceived;
	
	public CamShiftGui() {
		setTitle("Camshift");
		setLayout(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();
		setResizable(false);
		
		addWindowListener(this);
		
		rectangle = new Rect(100,100,100,100);
		camShiftAlgEnabled = false;
		camShiftAlg = new CamShiftAlg();
		lastFrameReceived = null;
		
		videoIcon = new JLabel();
		videoIcon.setPreferredSize(new Dimension(WebcamManager.WEBCAM_PX_WIDTH, WebcamManager.WEBCAM_PX_HEIGHT));
		
		c.fill = GridBagConstraints.HORIZONTAL;
		c.gridx = 0;
		c.gridy = 0;
		c.gridwidth = 8;
		add(videoIcon, c);
		
		xTextField = new JTextField();
		xTextField.setToolTipText("x");
		xTextField.setText("0");
		xTextField.setActionCommand("SetCoordinates");
		xTextField.getDocument().addDocumentListener(this);
		yTextField = new JTextField();
		yTextField.setToolTipText("y");
		yTextField.setText("0");
		yTextField.setActionCommand("SetCoordinates");
		yTextField.getDocument().addDocumentListener(this);
		widthTextField = new JTextField();
		widthTextField.setToolTipText("width");
		widthTextField.setText("0");
		widthTextField.setActionCommand("SetCoordinates");
		widthTextField.getDocument().addDocumentListener(this);
		heightTextField = new JTextField();
		heightTextField.setToolTipText("height");
		heightTextField.setText("0");
		heightTextField.setActionCommand("SetCoordinates");
		heightTextField.getDocument().addDocumentListener(this);
		
		x = new JLabel("X: ");
		y = new JLabel("Y: ");
		width = new JLabel("W: ");
		height = new JLabel("H: ");
		
		c.gridwidth = 1;
		c.gridy = 1;
		c.gridx = 0;		
		add(x,c);
		c.gridx = 2;
		add(y,c);
		c.gridx = 4;
		add(width, c);
		c.gridx = 6;
		add(height, c);
		
		c.weightx = 0.25;		
		c.gridx = 1;
		add(xTextField, c);		
		c.gridx = 3;
		add(yTextField, c);
		c.gridx = 5;
		add(widthTextField, c);
		c.gridx = 7;
		add(heightTextField, c);
		
		startButton = new JButton("Start");
		startButton.setActionCommand("StartTracking");
		startButton.addActionListener(this);
		c.gridwidth = 4;
		c.gridy = 2;
		c.gridx = 0;
		c.weightx = 0.5;
		add(startButton, c);
		
		configureButton = new JButton("Configure");
		configureButton.setActionCommand("Configure");
		configureButton.addActionListener(this);
		c.gridwidth = 4;
		c.gridy = 2;
		c.gridx = 4;
		c.weightx = 0.5;
		add(configureButton, c);
		
		configWindow = new ConfigurationGui();
		configWindow.addConfigurationListener(this);
		lowerb = new Scalar(0, 0, 0);
		upperb = new Scalar(0, 0, 0);
		
		videoSelection = new JComboBox<String>();
		videoSelection.addItem("Normal");
		videoSelection.addItem("Back Projection");
		videoSelection.addItem("Mask");
		videoSelection.addItem("Hue");
		videoSelection.addActionListener(this);
		c.gridwidth = 8;
		c.gridy = 3;
		c.gridx = 0;
		c.weightx = 1;
		add(videoSelection, c);
		
		pack();
		setDefaultCloseOperation(EXIT_ON_CLOSE);
		setVisible(true);
	}

	public void startCamera() {
		webcam = new WebcamManager(0);
		webcam.addWebcamListener(this);
		webcam.start();
	}
	
	@Override
	public void actionPerformed(ActionEvent e) {
		if(e.getActionCommand().equals("StartTracking")) {
			if (lastFrameReceived != null && rectangle.area() > 0) {
				camShiftAlg.setup(lastFrameReceived, rectangle, lowerb, upperb);
				
				camShiftAlgEnabled = true;
				
				startButton.setText("Stop");
				startButton.setActionCommand("StopTracking");
				
				xTextField.setEditable(false);
				yTextField.setEditable(false);
				heightTextField.setEditable(false);
				widthTextField.setEditable(false);
			}
		} else if (e.getActionCommand().equals("StopTracking")) {
			startButton.setText("Start");
			startButton.setActionCommand("StartTracking");
			
			camShiftAlgEnabled = false;
			
			xTextField.setEditable(true);
			yTextField.setEditable(true);
			heightTextField.setEditable(true);
			widthTextField.setEditable(true);
		} else if (e.getActionCommand().equals("Configure")) {
			configWindow.setVisible();
			
		}
	}
	
	public static void main(String args[]) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		CamShiftGui gui = new CamShiftGui();
		gui.startCamera();
	}

	@Override
	public void receiveWebcamFrame(Mat aFrame) {
		
//		if (configWindow.isVisible()) {
//			aFrame = CamShiftAlg.getMask(aFrame, lowerb, upperb);
//		}
		
		if (camShiftAlgEnabled) {
			rectangle = camShiftAlg.calcCamShiftedRect(aFrame);
			//Rect shiftedRect = camShiftAlg.calcMeanShiftedRect(aFrame);
			
			//aFrame = camShiftAlg.getHistogramBackProject(aFrame);
			
			//aFrame = CommonFunctions.drawRect(aFrame, shiftedRect);
		} else {
			lastFrameReceived = aFrame.clone();
		}
		
		if (videoSelection.getSelectedItem().toString().equals("Normal")) {
			
		} else if (videoSelection.getSelectedItem().toString().equals("Back Projection")) {
			aFrame = camShiftAlg.getHistogramBackProject(aFrame);
		} else if (videoSelection.getSelectedItem().toString().equals("Mask")) {
			aFrame = CamShiftAlg.getMask(aFrame, lowerb, upperb);
		} else if (videoSelection.getSelectedItem().toString().equals("Hue")) {
			aFrame = CamShiftAlg.getHueSpace(aFrame);
		}
		
		aFrame = CommonFunctions.drawRect(aFrame, rectangle);
		ImageIcon frame = new ImageIcon(CommonFunctions.bufferedImage(aFrame));
		
		videoIcon.setIcon(frame);
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
		
		webcam.terminateWebcam();

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

	@Override
	public void changedUpdate(DocumentEvent arg0) {

	}

	@Override
	public void insertUpdate(DocumentEvent arg0) {
		try {
			int x = Integer.parseInt(xTextField.getText());
			int y = Integer.parseInt(yTextField.getText());
			int width = Integer.parseInt(widthTextField.getText());
			int height = Integer.parseInt(heightTextField.getText());

			rectangle = new Rect(x,y,width,height);
		} catch (NumberFormatException exception) {
			rectangle = new Rect(0,0,0,0);
		}
	}

	@Override
	public void removeUpdate(DocumentEvent arg0) {
		try {
			int x = Integer.parseInt(xTextField.getText());
			int y = Integer.parseInt(yTextField.getText());
			int width = Integer.parseInt(widthTextField.getText());
			int height = Integer.parseInt(heightTextField.getText());

			rectangle = new Rect(x,y,width,height);
		} catch (NumberFormatException exception) {
			rectangle = new Rect(0,0,0,0);
		}
	}

	@Override
	public void receiveConfiguration(Scalar aLowerb, Scalar aUpperb) {
		System.out.println("Upperb: r:" + aUpperb.val[0] + " b: " + aUpperb.val[1] + " g: " + aUpperb.val[2]);
		System.out.println("Lowerb: r:" + aLowerb.val[0] + " b: " + aLowerb.val[1] + " g: " + aLowerb.val[2]);
		lowerb = aLowerb;
		upperb = aUpperb;
		if (rectangle.area() > 0) {
			camShiftAlg.setup(lastFrameReceived, rectangle, lowerb, upperb);
			System.out.println("Update Histogram");
		}
	}
	@Override
	public void endConfiguration() {
		System.out.println("");
		
	}
}
