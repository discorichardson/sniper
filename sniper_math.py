import math

focal_length=1.0

def set_focal_length(f):
	global focal_length
	focal_length=f

def get_width(pixels,distance):
	return pixels*distance/focal_length

def get_distance(pixels,width):
	return focal_length*width/pixels

def get_angle(pixels,distance):
	width=get_width(pixels,distance)
	return math.degrees(math.atan(width/distance))
