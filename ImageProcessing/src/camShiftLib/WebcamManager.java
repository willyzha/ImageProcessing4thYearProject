package camShiftLib;

import java.util.ArrayList;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.core.Mat;

public class WebcamManager{
	public static final int WEBCAM_PX_WIDTH = 680;
	public static final int WEBCAM_PX_HEIGHT =  420;
	
	private VideoCapture capture;
	private int deviceId;
	private Thread webcamThread;
	private ArrayList<WebcamListener> webcamListeners;
	private boolean start;
	
	public WebcamManager(int aDeviceId) {
		deviceId = aDeviceId;
		capture = new VideoCapture(deviceId);
		capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
		capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
		
		webcamListeners = new ArrayList<WebcamListener>();
	}
	
	public void start() {	
		webcamThread = new Thread() {
			public void run() {
				start = true;
				Mat image = new Mat();
				while (true && start) {
					if (capture.read(image)) {
						for (WebcamListener webcamListener: webcamListeners) {
							webcamListener.receiveWebcamFrame(image);
						}
					}
				}
				capture.release();
			}
		};
		
		webcamThread.run();
	}
	
	public Mat getFrame() {
		Mat image = new Mat();
		if (capture.read(image)) {
			return image;
		}
		return null;
	}
	
	public void addWebcamListener(WebcamListener aListener) {
		webcamListeners.add(aListener);
	}
	
	public void terminateWebcam() {
		start = false;
		
		while(webcamThread.isAlive()) {
			// Wait for webcamThread to finish
		}
	}
	
}
