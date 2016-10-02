package camShiftLib;

import java.util.ArrayList;
import java.util.List;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfFloat;
import org.opencv.core.MatOfInt;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.core.TermCriteria;
import org.opencv.highgui.Highgui;
import org.opencv.highgui.VideoCapture;
import org.opencv.imgproc.Imgproc;
import org.opencv.video.Video;

public class CamShiftAlg {
	
	private Mat roi_hist;
    private MatOfInt channels;
    private MatOfFloat ranges;
    private boolean setupComplete;
    private TermCriteria criteria;
    private Rect trackWindow;
	
	public CamShiftAlg() {
		channels = new MatOfInt(0);
		ranges = new MatOfFloat(0f, 180f);
		setupComplete = false;
		criteria = new TermCriteria(TermCriteria.COUNT + TermCriteria.EPS, 10, 1);
		trackWindow = null;
	}
	
	public void setup(Mat image, Rect startRect, Scalar lowerb, Scalar upperb) {
		
		trackWindow = startRect;
		
		Mat hsvImg_ROI = new Mat();
		Mat roi = image.submat(startRect);
		
		Imgproc.cvtColor(roi, hsvImg_ROI, Imgproc.COLOR_BGR2HSV);
		
		//Scalar lowerb = new Scalar(0, 60, 32);
		//Scalar upperb = new Scalar(180, 255, 255);
		
		Mat mask = new Mat();
		Core.inRange(hsvImg_ROI, lowerb, upperb, mask);

		Mat K = new Mat(new Size(3,3), CvType.CV_8UC1, new Scalar(1));
		Imgproc.erode(mask, mask, K);
		Imgproc.dilate(mask, mask, K);
		
		Highgui.imwrite("mask.jpg", mask);
		Highgui.imwrite("roi.jpg", hsvImg_ROI);
		
	    MatOfInt histSize = new MatOfInt(180);		    

	    List<Mat> hsvImg_ROI_List = new ArrayList<Mat>();
	    roi_hist = new Mat();
	    hsvImg_ROI_List.add(hsvImg_ROI);
		Imgproc.calcHist(hsvImg_ROI_List, channels, mask, roi_hist, histSize, ranges);
		
		Core.normalize(roi_hist, roi_hist, 0, 255, Core.NORM_MINMAX);
		
		setupComplete = true;
	}
	
	public static Mat getMask(Mat image, Scalar lowerb, Scalar upperb) {
		Mat hsvImg = new Mat();
		Imgproc.cvtColor(image, hsvImg, Imgproc.COLOR_BGR2HSV);
		
		//Scalar upperb = new Scalar(180, 255, 255);
		
		Mat mask = new Mat();
		Core.inRange(hsvImg, lowerb, upperb, mask);
		
		Mat K = new Mat(new Size(3,3), CvType.CV_8UC1, new Scalar(1));
		
		//System.out.println(K.toString());
		
		Imgproc.erode(mask, mask, K);
		Imgproc.dilate(mask, mask, K);
		
		return mask;
	}
	
	public RotatedRect calcCamShiftedRect(Mat image) {
		Mat hsv = new Mat();
		Mat dst = new Mat();
		
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		
		Highgui.imwrite("backProject.jpg", dst);
		
		RotatedRect newWindow = Video.CamShift(dst, trackWindow, criteria);
		trackWindow = newWindow.boundingRect();
		return newWindow;
	}
	
	public Rect calcMeanShiftedRect(Mat image) {
		Mat hsv = new Mat();
		Mat dst = new Mat();
		
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		Highgui.imwrite("backProject.jpg", dst);
		
		Video.meanShift(dst, trackWindow, criteria);
		
		return trackWindow;
	}
}
