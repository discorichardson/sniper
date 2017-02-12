import picamera #sudo apt-get install python-picamera
import picamera.array
import cv2 #sudo apt-get install libopencv-dev python-opencv python-dev
import sniper_math as sm
from Adafruit_PWM_Servo_Driver import PWM #git clone https://github.com/adafruit/Adafruit-Raspberry-Pi-Python=Code.git
from time import sleep
import RPi.GPIO as GPIO

laser_pin=21

ledr=6
ledg=5
ledb=4
ledx=0

def set_rgb(led):
    pwm.setPWM(ledr,4095,0)
    pwm.setPWM(ledg,4095,0)
    pwm.setPWM(ledb,4095,0)
    if led!=ledx:
        pwm.setPWM(led,0,4095)

GPIO.setmode(GPIO.BCM)
GPIO.setup(laser_pin,GPIO.OUT)
GPIO.output(laser_pin, False)

#TODO General code review
#TODO alternative, accept command line parameters
#TODO Doesn't seem to move correctly if target directly above centre
#TODO Tendancy to not track if target slightly above centre point

# window true if running in x so can show window
window=True
# lowres True to use low res image, False to use higher res image
# low res is quicker to process
lowres=False
# Enable laser fire
enable_laser=False

target_width=160 #mm

if enable_laser:
    print 'LASER ENABLED'

if lowres:
    print 'lowres'
    # resx, image width in pixels
    resx=160
    # resy, image height in pixels
    resy=120
    # killzone, size of area in pixels that is considered on target
    killzone=5
    # Set focal length used for calculations
    # I can't remember how I came up with these figures!
    sm.set_focal_length(157.0)
else:
    print 'highres'
    resx=320
    resy=240
    killzone=10
    sm.set_focal_length(316.0)

#print sm.focal_length

# centre of horizontal hunting arc
anglex_center=90
# far right
anglex_min=anglex_center-45
# far left
anglex_max=anglex_center+45
# current horizontal angle of turret
anglex=anglex_center
# centre of vertical hunting arc
angley_center=60
# top
angley_min=angley_center-45
# bottom
angley_max=angley_center
# current vertical angle of turret
angley=angley_center

# amount to move while hunting
huntd=16
# start looking left
huntx=huntd
# start looking up
hunty=-huntd

# Set up pwm
pwm=PWM(0x40)
pwm.setPWMFreq(50)

# If in windowed environment open a window with image preview
if window:
    cv2.namedWindow('image',cv2.WINDOW_NORMAL)

with picamera.PiCamera() as camera:
    #Set Camera settings
    camera.resolution=(resx,resy)
    #camera.iso=800
    #camera.shutter_speed=250000
    #camera.exposure_mode='off'
    #camera.awb_mode='off'

    #if not window:
    #    camera.start_preview()

    # Give camera time to warm up
    sleep(2)

    # It isn't over till it's finished
    finished=False
    # Set acquired if target detected
    acquired=False
    # Set confirmed if target in centre of image
    confirmed=False

    set_rgb(ledb)
    while not finished:
        # Turn camera led on if target acquired
        camera.led=acquired
        # Fire laser if target found
        GPIO.output(laser_pin, confirmed and enable_laser)

        #take photo
        with picamera.array.PiRGBArray(camera) as stream:
            #camera.capture(stream,format='bgr',use_video_port=True)
            camera.capture(stream,format='bgr')
            image=stream.array

        GPIO.output(laser_pin, False)

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

        #draw rectangles around found targets
        xt,yt,wt,ht=-1,-1,-1,-1
        for(x,y,w,h) in targets:
            if window:
                # Our target will end up being green or red,
                # any targets we're ignoring will be blue.
                cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2) #blue
            if h>ht:
                #save data on largest target found
                xt,yt,wt,ht=x,y,w,h

        acquired=False
        confirmed=False
        # If we've found a target
        if xt>-1:
            acquired=True
            # targetx,targety are coordinates of selected target
            targetx=xt+wt/2
            targety=yt+ht/2
            # Get distance from camera to target
            distance=sm.get_distance(wt,target_width)
            #print distance/1000
            # is centre of target in our kill zone?
            if abs(targetx-resx/2)<killzone and abs(targety-resy/2)<killzone:
                confirmed=True
                if window:
                    cv2.rectangle(image,(xt,yt),(xt+wt,yt+ht),(0,0,255),2) #red
            else:
                #off target
                if window:
                    cv2.rectangle(image,(xt,yt),(xt+wt,yt+ht),(0,255,0),2) #green

            # following calcs add distance from hinge for calculation
            if targetx<resx/2:
                if not confirmed: print 'left'
                anglex+=sm.get_angle(resx/2-targetx,distance+40)
            elif targetx>resx/2:
                if not confirmed: print 'right'
                anglex-=sm.get_angle(targetx-resx/2,distance+40)
            if targety>resy/2:
                if not confirmed: print 'down'
                angley+=sm.get_angle(targety-resy/2,distance+20)
            elif targety<resy/2:
                if not confirmed: print 'up'
                angley-=sm.get_angle(resy/2-targety,distance+20)
        else:
            # If no image acquired then keep searching for an image!
            anglex+=huntx
            if huntx>0 and anglex>anglex_max or huntx<0 and anglex<anglex_min:
                huntx=-huntx
                angley+=hunty
                if hunty>0 and angley>angley_max or hunty<0 and angley<angley_min:
                    hunty=-hunty

        # Don't allow us to go off hte range
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
            set_rgb(ledr)
        elif acquired:
            print 'Target Acquired'
            set_rgb(ledg)
        else:
            print 'Hunting...'
            set_rgb(ledb)

        #FIXME I should calibrate following equation to my servos
        pulse_len=int(float(anglex)*210.0/90.0)+184
        pwm.setPWM(0,0,pulse_len) #side movement 26=right center=103 180=left
        pulse_len=int(float(angley)*210.0/90.0)+184
        pwm.setPWM(2,0,pulse_len) #vertical bottom=122 center=82 top=42

        #save image
        #cv2.imwrite('result.jpg',image)

        if window:
            #show image
            cv2.imshow('image',cv2.flip(image,1))
            # If user hits escape then stop everything
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

    set_rgb(ledx)
