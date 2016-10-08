package camShiftLib;

import org.opencv.core.Scalar;

public interface ConfigurationListener {
	public void receiveConfiguration(Scalar lowerb, Scalar upperb);
	
	public void endConfiguration();
}
