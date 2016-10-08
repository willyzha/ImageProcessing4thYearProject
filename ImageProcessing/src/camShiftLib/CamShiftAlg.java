package camShiftLib;

import java.util.ArrayList;
import java.util.List;

import javax.imageio.ImageWriter;

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
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.video.Video;

public class CamShiftAlg {
	
	private Mat roi_hist;
    private MatOfInt channels;
    private MatOfFloat ranges;
    private boolean setupComplete;
    private TermCriteria criteria;
    private Rect trackWindow;
    MatOfInt histSize;
	
	public CamShiftAlg() {
		channels = new MatOfInt(0);
		ranges = new MatOfFloat(0f, 180f);
		setupComplete = false;
		criteria = new TermCriteria(TermCriteria.COUNT + TermCriteria.EPS, 10, 1);
		trackWindow = null;
		histSize = new MatOfInt(16);	
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

		Mat K = new Mat(new Size(2,2), CvType.CV_8UC1, new Scalar(1));
//		Imgproc.erode(mask, mask, K);
//		Imgproc.dilate(mask, mask, K);
		
		Imgcodecs.imwrite("mask.jpg", mask);
		Imgcodecs.imwrite("roi.jpg", hsvImg_ROI);	    

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
		
		Mat K = new Mat(new Size(2,2), CvType.CV_8UC1, new Scalar(1));
		
		//System.out.println(K.toString());
		
//		Imgproc.erode(mask, mask, K);
//		Imgproc.dilate(mask, mask, K);
		
		return mask;
	}
	
	public Mat getHistogramBackProject(Mat image) {
		Mat hsv = new Mat();
		Mat dst = new Mat();
		
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		return dst;
	}
	
	public static Mat getHueSpace(Mat image) {
		Mat hsv = new Mat();
		Mat H = new Mat();
		Mat S = new Mat();
		Mat V = new Mat();
		ArrayList<Mat> channels = new ArrayList<Mat>();
		channels.add(H);
		channels.add(S);
		channels.add(V);
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		System.out.println("Dims: " + hsv.dims());
		Core.split(hsv, channels);
		
		channels.get(1).setTo(new Scalar(0));
		channels.get(2).setTo(new Scalar(0));
		
		Core.merge(channels, hsv);
		
		return hsv;
	}
	
	public Rect calcCamShiftedRect(Mat image) {
		Mat hsv = new Mat();
		Mat dst = new Mat();
		
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		
		Imgcodecs.imwrite("backProject.jpg", dst);
		
		Rect tempTrackWindow = trackWindow.clone();
		
		RotatedRect newWindow = Video.CamShift(dst, trackWindow, criteria);
		//trackWindow = newWindow.boundingRect();
		
		if (trackWindow.area() == 0) {
			trackWindow = tempTrackWindow;
		}
		
		return trackWindow;
	}
	
	public Rect calcMeanShiftedRect(Mat image) {
		Mat hsv = new Mat();
		Mat dst = new Mat();
		
		Imgproc.cvtColor(image, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		Imgcodecs.imwrite("backProject.jpg", dst);
		
		Video.meanShift(dst, trackWindow, criteria);
		
		return trackWindow;
	}
}
