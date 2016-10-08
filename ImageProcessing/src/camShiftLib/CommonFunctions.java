package camShiftLib;

import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;

import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.RotatedRect;
import org.opencv.core.Scalar;
import org.opencv.imgproc.Imgproc;

public class CommonFunctions {
	
	public static BufferedImage bufferedImage(Mat m) {
	    int type = BufferedImage.TYPE_BYTE_GRAY;
	    if ( m.channels() > 1 ) {
	        type = BufferedImage.TYPE_3BYTE_BGR;
	    }
	    BufferedImage image = new BufferedImage(m.cols(),m.rows(), type);
	    m.get(0,0,((DataBufferByte)image.getRaster().getDataBuffer()).getData()); // get all the pixels
	    return image;
	}
	
	public static Mat drawRect(Mat m, Rect rect) {
		Mat markedupImage = m.clone();
		Imgproc.rectangle(markedupImage, 
				new Point(rect.x, rect.y), 
				new Point(rect.x + rect.width, rect.y + rect.height),
				new Scalar(0, 255, 0));
		return markedupImage;
	}
	
	public static Mat drawRect(Mat m, RotatedRect rect) {
		Mat markedupImage = m.clone();
		Point[] pt = new Point[4];
		rect.points(pt);
		
		Scalar color = new Scalar(0, 255, 0);
		
		Imgproc.line(markedupImage, 
				pt[0], pt[1], color);
		Imgproc.line(markedupImage, 
				pt[1], pt[2], color);
		Imgproc.line(markedupImage, 
				pt[2], pt[3], color);
		Imgproc.line(markedupImage, 
				pt[3], pt[0], color);
		
		return markedupImage;
	}

}
