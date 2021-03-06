package test;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.CascadeClassifier;

public class Hello
{
	private static final int WEBCAM_PX_HEIGHT = 720;
	private static final int WEBCAM_PX_WIDTH = 1280;
	public void run() {
		Mat image = Imgcodecs.imread("webcamOut.png");
		CascadeClassifier circleDetector = new CascadeClassifier("cascade.xml");

		MatOfRect detections = new MatOfRect();
		circleDetector.detectMultiScale(image, detections);

		System.out.println(String.format("Detected %s faces", detections.toArray().length));

		for (Rect rect : detections.toArray()) {
			Imgproc.rectangle(image, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));
		}

		// Save the visualized detection.
		String filename = "faceDetection.png";
		System.out.println(String.format("Writing %s", filename));
		Imgcodecs.imwrite(filename, image);


	}

	public void webcamCapture() {
		VideoCapture capture = new VideoCapture(0);
		capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
		capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);

		capture.open(0);
		System.out.println(capture.isOpened());

		Mat image = new Mat();
		if (capture.read(image)) {
			//Imgproc.resize(image, image, new Size(240, 240), 0, 0, Imgproc.INTER_CUBIC);
			System.out.println("Sucessful");
			String filename = "webcamOut.png";
			Imgcodecs.imwrite(filename, image);
		}	  

		System.out.println("Fail");
	}

	public static void main(String[] args) {
		System.out.println("Hello, OpenCV");
		// Load the native library.
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);

		Hello test = new Hello();

		test.webcamCapture();
		test.run();		  

	}
}

