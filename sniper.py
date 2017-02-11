import picamera #sudo apt-get install python-picamera
import picamera.array
import cv2 #sudo apt-get install libopencv-dev python-opencv python-dev
import sniper_math as sm
from Adafruit_PWM_Servo_Driver import PWM #git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python=Code.git
from time import sleep
import RPi.GPIO as GPIO

laser_pin=21

GPIO.setmode(GPIO.BCM)
GPIO.setup(laser_pin,GPIO.OUT)
GPIO.output(laser_pin, False)

#TODO method of working out if running in X
window=True
lowres=False

target_width=160 #mm

if lowres:
	resx=160
	resy=120
	killzone=5
	sm.set_focal_length(157.0)
else:
	resx=320
	resy=240
	killzone=10
	sm.set_focal_length(316.0)
	
#print sm.focal_length
	
anglex_center=90
anglex_min=anglex_center-45 #Far right
anglex_max=anglex_center+45 #far left
anglex=anglex_center
angley_center=60
angley_min=angley_center-30 #top
angley_max=angley_center+10 #bottom
angley=angley_center

huntd=16
huntx=huntd #start looking left
hunty=-huntd #start looking up

pwm=PWM(0x40)
pwm.setPWMFreq(50)
if window:
	cv2.namedWindow('image',cv2.WINDOW_NORMAL)

with picamera.PiCamera() as camera:
	camera.resolution=(resx,resy)
	#camera.iso=800
	#camera.shutter_speed=250000
	#camera.exposure_mode='off'
	#camera.awb_mode='off'

	#if not window:
	#	camera.start_preview()

	sleep(2)

	finished=False
	acquired=False
	confirmed=False
	while not finished:
		#camera.led=acquired
		GPIO.output(laser_pin, confirmed)
		#take photo
		with picamera.array.PiRGBArray(camera) as stream:
			#camera.capture(stream,format='bgr',use_video_port=True)
			camera.capture(stream,format='bgr')
			image=stream.array

		GPIO.output(laser_pin, False)
		#camera.led=False
	
		if window:
			cv2.imshow('image',cv2.flip(image,1))
			cv2.waitKey(1)

		#load classifier
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt.xml')
		target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml')
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_alt_tree.xml') #SLOW
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_profileface.xml') #DIDN'T FIND ME
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_mcs_upperbody.xml') #SLOW
		#target_cascade=cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_upperbody.xml') #DIDN'T FIND ME
		
		#convert to gray
		gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	
		#detect targets
		targets=target_cascade.detectMultiScale(gray,1.1,5)
		
		#draw rectangles
		xt,yt,wt,ht=-1,-1,-1,-1
		for(x,y,w,h) in targets:
			if window:
				cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2) #blue
			if h>ht:
				#save data on largest target found
				xt,yt,wt,ht=x,y,w,h
			
		acquired=False
		confirmed=False
		if xt>-1:
			acquired=True
			targetx=xt+wt/2
			targety=yt+ht/2
			distance=sm.get_distance(wt,target_width)
			print distance/1000
			if abs(targetx-resx/2)<killzone and abs(targety-resy/2)<killzone:
				confirmed=True
				#on target
				#camera.led=True
				if window:
					cv2.rectangle(image,(xt,yt),(xt+wt,yt+ht),(0,0,255),2) #red
			else:
				#off target
				if window:
					cv2.rectangle(image,(xt,yt),(xt+wt,yt+ht),(0,255,0),2) #green
			
			#following calcs add distance from hinge for calculation
			if targetx<resx/2:
				#anglex+=(resx/2-targetx)/6
				anglex+=sm.get_angle(resx/2-targetx,distance+40)
			elif targetx>resx/2:
				#anglex-=(targetx-resx/2)/6
				anglex-=sm.get_angle(targetx-resx/2,distance+40)
			if targety>resy/2:
				#angley+=(targety-resy/2)/6
				angley+=sm.get_angle(targety-resy/2,distance+20)
			elif targety<resy/2:
				#angley-=(resy/2-targety)/6
				angley-=sm.get_angle(resy/2-targety,distance+20)
		else:
			anglex+=huntx
			if huntx>0 and anglex>anglex_max or huntx<0 and anglex<anglex_min:
				huntx=-huntx
				angley+=hunty
				if hunty>0 and angley>angley_max or hunty<0 and angley<angley_min:
					hunty=-hunty
			
		if anglex>anglex_max:
			anglex=anglex_max
		if anglex<anglex_min:
			anglex=anglex_min
		if angley>angley_max:
			angley=angley_max
		if angley<angley_min:
			angley=angley_min
			
		if confirmed:
			print 'Confirmed Shot'
		elif acquired:
			print 'Target Acquired'
		else:
			print 'Hunting...'

		#TODO I should calibrate following equation to my servos
		pulse_len=int(float(anglex)*210.0/90.0)+184
		pwm.setPWM(0,0,pulse_len) #side movement 26=right center=103 180=left
		pulse_len=int(float(angley)*210.0/90.0)+184
		pwm.setPWM(2,0,pulse_len) #vertical bottom=122 center=82 top=42
	
		#save image
		#cv2.imwrite('result.jpg',image)
	
		if window:
			#show image
			cv2.imshow('image',cv2.flip(image,1))
			if cv2.waitKey(100)==27:
				finished=True
		else:
			sleep(0.1)
	
	if window:
		cv2.destroyWindow('image')

	#Centre Camera
	pulse_len=int(float(anglex_center)*210.0/90.0)+184
	pwm.setPWM(0,0,pulse_len) #side movement 26=right center=103 180=left
	pulse_len=int(float(angley_center)*210.0/90.0)+184
	pwm.setPWM(2,0,pulse_len) #vertical bottom=122 center=82 top=42
