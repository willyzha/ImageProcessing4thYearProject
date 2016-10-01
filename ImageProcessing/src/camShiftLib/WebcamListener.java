package camShiftLib;

import java.awt.event.ActionListener;

import org.opencv.core.Mat;

public interface WebcamListener extends ActionListener {
	
	public void receiveWebcamFrame(Mat aFrame);
	
}
