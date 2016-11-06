import numpy as np
import matplotlib.pyplot as plt
import cv2

# Random gaussian data.

def plotHsvHist(hist):

    #n
    #hist = [  2.55000000e+02,   2.43992813e+02,   1.18356931e+02,   1.18356928e-01,   2.00000000e+02,   2.01206779e+02,   2.00000000e+02,   2.00000000e+02,   1.18356928e-01,   5.32606184e-01,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   1.10071945e+01]
    #bins
    histBins = np.linspace(0,255,len(hist))
    #print data
    # This is  the colormap I'd like to use.
    cm = plt.cm.get_cmap('hsv')
    
    # Plot histogram.
    #n, bins, patches = plt.hist(data, 25, normed=1, color='green')
    n, bins, patches = plt.hist(histBins, weights=hist, bins=histBins)
    
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    
    # scale values to interval [0,1]
    col = bin_centers - min(bin_centers)
    col /= max(col)
    
    for c, p in zip(col, patches):
        #print c, p
        plt.setp(p, 'facecolor', cm(c))
        plt.axis([0, 255, 0, 255])
        plt.xticks(bins)
    
    fig = plt.figure(1)
    fig.canvas.draw()
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    data = cv2.cvtColor(data, cv2.COLOR_RGB2BGR)

    return data

if __name__ == "__main__":
    testHist = [  2.55000000e+02,   2.43992813e+02,   1.18356931e+02,   1.18356928e+01,   2.00000000e+02,   2.01206779e+02,   2.00000000e+02,   2.00000000e+02,   1.18356928e+01,   5.32606184e+01,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   2.00000000e+02,   1.10071945e+01]
    plotHsvHist(testHist)
    
    