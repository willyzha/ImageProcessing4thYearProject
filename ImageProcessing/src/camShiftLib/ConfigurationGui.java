package camShiftLib;

import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.util.ArrayList;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JSlider;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import org.opencv.core.Scalar;

public class ConfigurationGui extends JFrame implements ChangeListener, WindowListener{
	
	private static final long serialVersionUID = 6825758062558727590L;
	JSlider lowerR;
	JSlider lowerB;
	JSlider lowerG;
	
	JSlider upperR;
	JSlider upperB;
	JSlider upperG;
	
	ArrayList<ConfigurationListener> configurationListeners = new ArrayList<ConfigurationListener>();
	
	public ConfigurationGui() {
		setTitle("Camshift");
		setLayout(new GridBagLayout());
		GridBagConstraints c = new GridBagConstraints();
		setResizable(false);
		
		c.fill = GridBagConstraints.HORIZONTAL;
		c.gridx = 0;
		c.gridy = 0;
		c.gridwidth = 2;
		add(new JLabel("LowerRange"), c);
		
		c.gridwidth = 1;
		c.gridy = 1;
		c.gridx = 0;
		add(new JLabel("R: "), c);		
		c.gridx = 1;
		lowerR = new JSlider(0, 255, 128);
		lowerR.addChangeListener(this);
		lowerR.setMajorTickSpacing(85);
		lowerR.setMinorTickSpacing(17);
		lowerR.setPaintTicks(true);
		lowerR.setPaintLabels(true);
		add(lowerR, c);
		
		c.gridy = 2;
		c.gridx = 0;
		add(new JLabel("B: "), c);		
		c.gridx = 1;
		lowerB = new JSlider(0, 255, 72);
		lowerB.addChangeListener(this);
		lowerB.setMajorTickSpacing(85);
		lowerB.setMinorTickSpacing(17);
		lowerB.setPaintTicks(true);
		lowerB.setPaintLabels(true);
		add(lowerB, c);
		
		c.gridy = 3;
		c.gridx = 0;
		add(new JLabel("G: "), c);		
		c.gridx = 1;
		lowerG = new JSlider(0, 255, 13);
		lowerG.addChangeListener(this);
		lowerG.setMajorTickSpacing(85);
		lowerG.setMinorTickSpacing(17);
		lowerG.setPaintTicks(true);
		lowerG.setPaintLabels(true);
		add(lowerG, c);
		
		c.gridy = 4;
		c.gridwidth = 2;
		add(new JLabel("UpperRange"), c);
		
		c.gridwidth = 1;
		c.gridy = 5;
		c.gridx = 0;
		add(new JLabel("R: "), c);		
		c.gridx = 1;
		upperR = new JSlider(0, 255, 255);
		upperR.addChangeListener(this);
		upperR.setMajorTickSpacing(85);
		upperR.setMinorTickSpacing(17);
		upperR.setPaintTicks(true);
		upperR.setPaintLabels(true);
		add(upperR, c);
		
		c.gridy = 6;
		c.gridx = 0;
		add(new JLabel("B: "), c);		
		c.gridx = 1;
		upperB = new JSlider(0, 255, 255);
		upperB.addChangeListener(this);
		upperB.setMajorTickSpacing(85);
		upperB.setMinorTickSpacing(17);
		upperB.setPaintTicks(true);
		upperB.setPaintLabels(true);
		add(upperB, c);
		
		c.gridy = 7;
		c.gridx = 0;
		add(new JLabel("G: "), c);		
		c.gridx = 1;
		upperG = new JSlider(0, 255, 255);
		upperG.addChangeListener(this);
		upperG.setMajorTickSpacing(85);
		upperG.setMinorTickSpacing(17);
		upperG.setPaintTicks(true);
		upperG.setPaintLabels(true);
		add(upperG, c);
		
		for(ConfigurationListener listener: configurationListeners) {
			listener.receiveConfiguration(new Scalar(lowerR.getValue(), lowerB.getValue(), lowerG.getValue()),
					new Scalar(upperR.getValue(), upperB.getValue(), upperG.getValue()));
		}
		
		pack();
	}
	
	public void setVisible() {
		for(ConfigurationListener listener: configurationListeners) {
			listener.receiveConfiguration(new Scalar(lowerR.getValue(), lowerB.getValue(), lowerG.getValue()),
					new Scalar(upperR.getValue(), upperB.getValue(), upperG.getValue()));;
		}
		setVisible(true);
	}
		
	public void addConfigurationListener(ConfigurationListener listener) {
		configurationListeners.add(listener);
	}
	
	public static void main(String args[]) {
		ConfigurationGui gui = new ConfigurationGui();
		gui.setVisible();
	}

	@Override
	public void stateChanged(ChangeEvent arg0) {
		for(ConfigurationListener listener: configurationListeners) {
			listener.receiveConfiguration(new Scalar(lowerR.getValue(), lowerB.getValue(), lowerG.getValue()),
					new Scalar(upperR.getValue(), upperB.getValue(), upperG.getValue()));
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
		for(ConfigurationListener listener: configurationListeners) {
			listener.receiveConfiguration(new Scalar(lowerR.getValue(), lowerB.getValue(), lowerG.getValue()),
					new Scalar(upperR.getValue(), upperB.getValue(), upperG.getValue()));
		}
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
