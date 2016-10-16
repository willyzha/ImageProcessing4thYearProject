package tools;

import java.util.ArrayList;
import java.util.List;

import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfFloat;
import org.opencv.core.MatOfInt;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;
import org.opencv.core.Scalar;
import org.opencv.core.TermCriteria;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.imgproc.Imgproc;
import org.opencv.video.Video;

public class CamShift {
	VideoCapture capture;
	private static final int WEBCAM_PX_WIDTH = 640;
	private static final int WEBCAM_PX_HEIGHT =  480;
	
	public CamShift() {
		capture = new VideoCapture(0);
		capture.set(Videoio.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_PX_HEIGHT);
		capture.set(Videoio.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_PX_WIDTH);
	}
	
	public void run() {	
		Mat inputImage = Imgcodecs.imread("stock.jpg");
		Imgcodecs.imwrite("input.png", inputImage);
		
		Mat roi = inputImage.submat(new Rect(240, 30, 140, 140));
		Imgcodecs.imwrite("roi.png", roi);
		
		Mat hsvImg_ROI = new Mat();			
		Imgproc.cvtColor(roi, hsvImg_ROI, Imgproc.COLOR_BGR2HSV);
		Imgcodecs.imwrite("hsvImg_ROI.png", hsvImg_ROI);
		
		Scalar lowerb = new Scalar(0, 60, 32);
		Scalar upperb = new Scalar(180, 255, 255);
		
		Mat mask = new Mat();		
		Core.inRange(hsvImg_ROI, lowerb, upperb, mask);
		Imgcodecs.imwrite("mask.png", mask);
		
//	    int hbins = 30, sbins = 32;
	    MatOfInt histSize = new MatOfInt(180);
	    Mat roi_hist = new Mat();
	    MatOfInt channels = new MatOfInt(0);
//	    double hranges[] = { 0, 180 };
//	    double sranges[] = { 0, 256 };
	    //double ranges[][] = { hranges, sranges };
	    MatOfFloat ranges = new MatOfFloat(0f, 180f);
	    List<Mat> hsvImg_ROI_List = new ArrayList<Mat>();
	    hsvImg_ROI_List.add(hsvImg_ROI);
		Imgproc.calcHist(hsvImg_ROI_List, channels, mask, roi_hist, histSize, ranges);
		
		Core.normalize(roi_hist, roi_hist, 0, 255, Core.NORM_MINMAX);
		
		TermCriteria criteria = new TermCriteria(TermCriteria.COUNT + TermCriteria.EPS, 10, 1);
		// *********************** //
		Mat hsv = new Mat();
		Mat dst = new Mat();
		Imgproc.cvtColor(inputImage, hsv, Imgproc.COLOR_BGR2HSV);
		List<Mat> hsv_list = new ArrayList<Mat>();
		hsv_list.add(hsv);
		Imgproc.calcBackProject(hsv_list, channels, roi_hist, dst, ranges, 1);
		
		Imgcodecs.imwrite("dst.png", dst);
		
		Rect trackWindow = new Rect(240, 30, 140, 140);
		
		Mat outputImage1 = inputImage.clone();	
		Imgproc.rectangle(outputImage1, 
				new Point(trackWindow.x, trackWindow.y), 
				new Point(trackWindow.x + trackWindow.width, trackWindow.y + trackWindow.height),
				new Scalar(0, 255, 0));
		Imgcodecs.imwrite("outputImage1.png", outputImage1);
		

		
		RotatedRect newWindow = Video.CamShift(dst, trackWindow, criteria);
		
		Mat markedupImage = inputImage.clone();	
		
		Imgproc.rectangle(markedupImage, 
				new Point(newWindow.boundingRect().x, newWindow.boundingRect().y), 
				new Point(newWindow.boundingRect().x + newWindow.boundingRect().width, 
						newWindow.boundingRect().y + newWindow.boundingRect().height),
				new Scalar(0, 255, 0));
		
		Imgcodecs.imwrite("markedupImage.png", markedupImage);
		//ArrayList<Mat> hsvImgList = new ArrayList<Mat>();
		//hsvImgList.add(hsvImg_ROI);
					
		
		//Imgproc.calcHist(hsvImgList, [0], mask, hist, histSize, ranges);
		

	}
	
	public static void main (String args[]) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		new CamShift().run();
	}
}
