package test;

import java.awt.Image;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import org.opencv.core.Core;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.highgui.Highgui;
import org.opencv.objdetect.CascadeClassifier;

public class Hello
{
	  public void run() {
		   Mat image = Highgui.imread("TestImage2.jpg");
		   CascadeClassifier circleDetector = new CascadeClassifier("cascade.xml");
		   
		   MatOfRect detections = new MatOfRect();
		   circleDetector.detectMultiScale(image, detections);
		   
		   System.out.println(String.format("Detected %s faces", detections.toArray().length));
		   
		    for (Rect rect : detections.toArray()) {
		        Core.rectangle(image, new Point(rect.x, rect.y), new Point(rect.x + rect.width, rect.y + rect.height), new Scalar(0, 255, 0));
		    }
		    
		    // Save the visualized detection.
		    String filename = "faceDetection.png";
		    System.out.println(String.format("Writing %s", filename));
		    Highgui.imwrite(filename, image);
	  }
	
	

	  public static void main(String[] args) {
		  System.out.println("Hello, OpenCV");
		  // Load the native library.
		  System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
		  new Hello().run();
	  }
   
   
   public Image toBufferedImage(Mat m){
       int type = BufferedImage.TYPE_BYTE_GRAY;
       if ( m.channels() > 1 ) {
           type = BufferedImage.TYPE_3BYTE_BGR;
       }
       int bufferSize = m.channels()*m.cols()*m.rows();
       byte [] b = new byte[bufferSize];
       m.get(0,0,b); // get all the pixels
       BufferedImage image = new BufferedImage(m.cols(),m.rows(), type);
       final byte[] targetPixels = ((DataBufferByte) image.getRaster().getDataBuffer()).getData();
       System.arraycopy(b, 0, targetPixels, 0, b.length);  
       return image;

   }
}

