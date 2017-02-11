import picamera #sudo apt-get install python-picamera
import picamera.array
import cv2 #sudo apt-get install libopencv-dev python-opencv python-dev
import numpy as np
from time import sleep

target_distance=600 #mm
target_width=298 #mm (Width of A4 sheet held landscape)

resx=160
resy=120

cv2.namedWindow('image',cv2.WINDOW_NORMAL)

with picamera.PiCamera() as camera:
	camera.resolution=(resx,resy)

	sleep(2)

	finished=False
	while not finished:
		#take photo
		with picamera.array.PiRGBArray(camera) as stream:
			camera.capture(stream,format='bgr',use_video_port=True)
			image=stream.array
	
		cv2.imshow('image',cv2.flip(image,1))
		if cv2.waitKey(500)==27:
				finished=True

		#convert to grey, blur, edge detect
		gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

		cv2.imshow('image',cv2.flip(gray,1))
		if cv2.waitKey(500)==27:
				finished=True

		gray=cv2.GaussianBlur(gray, (5,5), 0)

		cv2.imshow('image',cv2.flip(gray,1))
		if cv2.waitKey(500)==27:
				finished=True

		edged=cv2.Canny(gray, 35, 125)

		cv2.imshow('image',cv2.flip(edged,1))
		if cv2.waitKey(500)==27:
				finished=True

		# find contours, keep largest
		(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		c=max(cnts, key=cv2.contourArea)
		
		marker=cv2.minAreaRect(c)
		pixel_width=marker[1][0]
		
		box=np.int0(cv2.cv.BoxPoints(marker))
		cv2.drawContours(edged, [box], -1, (255,255,255), 2)

		f=(pixel_width * target_distance)/target_width
		print f

		cv2.imshow('image',cv2.flip(edged,1))
		if cv2.waitKey(0)==27:
				finished=True


	cv2.destroyWindow('image')
