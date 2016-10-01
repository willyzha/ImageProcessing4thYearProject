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
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;

public class CamShiftGui extends JFrame implements ActionListener, WebcamListener, WindowListener, DocumentListener{

	private static final long serialVersionUID = 2028612532446093868L;
	
	private JLabel videoIcon;
	private JButton startButton;
	private JLabel x;
	private JLabel y;
	private JLabel width;
	private JLabel height;
	private JTextField xTextField;
	private JTextField yTextField;
	private JTextField widthTextField;
	private JTextField heightTextField;
	
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
		
		rectangle = new Rect(0,0,0,0);
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
		width = new JLabel("Width: ");
		height = new JLabel("Height: ");
		
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
		c.gridwidth = 8;
		c.gridy = 2;
		c.gridx = 0;
		c.weightx = 1;
		add(startButton, c);
		
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
			if (lastFrameReceived != null) {
				camShiftAlg.setup(lastFrameReceived, rectangle);
				
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
		}
	}
	
	public static void main(String args[]) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		CamShiftGui gui = new CamShiftGui();
		gui.startCamera();
	}

	@Override
	public void receiveWebcamFrame(Mat aFrame) {
		if (camShiftAlgEnabled) {
			RotatedRect shiftedRect = camShiftAlg.calcShiftedRect(aFrame);
			aFrame = CommonFunctions.drawRect(aFrame, shiftedRect);
		} else {
			lastFrameReceived = aFrame.clone();
			aFrame = CommonFunctions.drawRect(aFrame, rectangle);
		}		
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
}
