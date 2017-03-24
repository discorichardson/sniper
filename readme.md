# sniper
Raspberry Pi Face hunting.  Once finshed should paint a Laser sight on a persons forehead.  Precautions should obviously be taken not to blind someone and *laser* can obviously be replaced with a simple LED to be on the safe side.  
This is a work in progress.

## Files
* calibrate.py  
Program to aid calibrating values for distance measurement and angles *TODO* Work out what I actually used this for
* sniper.py  
Program to seek faces and shoot at them with a *laser*
* sniper_math.py  
Library to compute width of an object, distance from camera and angle required to move a certain number of pixels

## Third party libraries required
* Adafruit_Python_PCA9685  
Adafruit library for controlling servo board PCA9685
```
git clone https://github.com/adafruit/Adafruit_Python_PCA9685.git
cd Adafruit_Python_PCA9685
sudo python setup.py install
```
or  
`sudo pip install adafruit-pca9685`
* picamera  
`sudo apt-get install python-picamera`
* cv2  
`sudo apt-get install libopencv-dev python-opencv python-dev`

## Hardware required
* Raspberry Pi  
Pi 2 or above, to allow for processing power when detecting faces
* Camera Module  
I use the original module, should work with newer variant
* Servo Control board  
I use the Adafruit PCA9685
* Other items
	* Servos * 2
	* Long camera ribbon
	* Turret
	* Case for Camera & laser
	* Laser
	* Power supplies for Pi and Servo board
	* Wires to connect

## Connections
* Connect camera to Raspberry Pi. Blue band towards eternet port.
* Connect Pi 5V pin to Servo Board V+ and Pi GND pin to Servo Board GND
* Connect Pi SDA pin 2 to Servo Board SDA pin
* Connect Pi SCL pin 3 to Servo Board SCL pin
* Connect Servo Board 1 to Servo controlling Left/Right movement
* Connect Servo Board 3 to Servo controlling Up/Down movement
* Connect Servo Board to 5v external power supply

## Further setup in Raspbian

### Test camera
Run `python testcamera.py` to test camera.  
This wil display a live feed from camera.

### Test opencv
Run `python testcv.py` to test cv installation.  
This will print version number.

## *TODO* List
Further requirements:

* Transistor to switch laser on and off (code done, not documented above)
* Safety switch to disable laser
* Case
* Power
* Mobile phone interface
