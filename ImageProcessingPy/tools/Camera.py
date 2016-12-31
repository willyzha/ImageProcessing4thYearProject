import cv2

resolution = [640, 480]
camera = cv2.VideoCapture(0)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

cv2.namedWindow("frame")

while True:   
    grabbed, frame = camera.read()
    
    cv2.imshow("frame", frame)
    
    #cv2.waitKey(1)
    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:
        break
    if ch == ord(' '):
        cv2.imwrite("pic.jpg", frame)