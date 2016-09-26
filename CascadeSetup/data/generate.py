import subprocess, sys, os

OPEN_CV_PATH = os.path.abspath(sys.argv[1])

negatives = os.listdir("neg")
positives = os.listdir("target")

file = open('negatives.txt', 'w')
for negativePic in negatives:
	if('.jpg' in negativePic or '.png' in  negativePic):
		negPath = os.getcwd()+"\\neg\\"+negativePic
		file.write(negPath+'\n')
file.close()
	
file = open('positives.txt', 'w')
for positivePic in positives:
	if('.jpg' in positivePic or '.png' in  positivePic):
		posPath = os.getcwd()+"\\target\\"+positivePic
		file.write(posPath+'\n')
file.close()

with open("positives.txt") as f:
	content = f.readlines()
	count = 0
	filenames = []
	print(content)
	for target in content:
		print(target)
		#subprocess.call('E:/openCV/opencv/build/x64/vc11/bin/opencv_createsamples.exe', shell=True)
		#E:/workspace/opencv-master/opencv-master/build/bin/Release/
		subprocess.call(OPEN_CV_PATH + '/build/x64/vc14/bin/opencv_createsamples.exe -bg negatives.txt -info data/annotations'+str(count)+'.lst -maxxangle 0.2 -maxyangle 0.2 -maxzangle 0.5 -bgthresh 40 -h 50 -w 75 -num 300 -img '+target, shell=True)
		filenames.append('data/annotations'+str(count)+'.lst')
		count = count + 1

	totalPositiveSamples = 0
	with open('data/annotations.lst', 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)
					totalPositiveSamples = totalPositiveSamples + 1
					
	subprocess.call(OPEN_CV_PATH + '/build/x64/vc14/bin/opencv_createsamples.exe -vec positiveVector.vec -info data/annotations.lst -num '+str(totalPositiveSamples)+' -h 50 -w 75', shell=True)
	
	subprocess.call(OPEN_CV_PATH + '/build/x64/vc14/bin/opencv_createsamples.exe -vec positiveVector.vec -h 50 -w 75', shell=True)
	
	#E:\openCV\opencv3.0\build\x64\vc14\bin\opencv_traincascade.exe -data cascadeData -vec presto.vec -bg negatives.txt -numPos 3000 -numNeg 1500 -numStages 20 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -h 50 -w 75 -numThreads 8 -precalcValBufSize 2048 -precalcIdxBufSize 2048

print(OPEN_CV_PATH + '\\build\\x64\\vc14\\bin\\opencv_traincascade.exe -data cascadeData -vec positiveVector.vec -bg negatives.txt -numPos 3000 -numNeg 1500 -numStages 20 -minHitRate 0.999 -maxFalseAlarmRate 0.5 -h 50 -2 75 -numThreads 8 -precalcValBufSize 2048 -precalcIdxBufSize 2048')