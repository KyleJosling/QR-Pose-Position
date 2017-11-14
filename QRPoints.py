import cv2
import math
import numpy as np
import glob

#This file searches and returns for the points in the QR code that are used
#to find the pose and position of the camera.


#This function gets two points from each corner square
def getSquarePoints(points,center):

	#Search for max and min distances, return the indices
	maxIndex=0
	maxVal=0
	minIndex=0
	minVal=distance(points[0][0],center)
	for i in range(0,4):
		cValue=distance(points[i][0],center)
		if cValue > maxVal:
			maxVal=cValue
			maxIndex=i
		if cValue<minVal:
			minVal=cValue
			minIndex=i
	return points[maxIndex][0],points[minIndex][0]


#Gets distance between two points
def distance(p,q):
	return math.sqrt(math.pow(math.fabs(p[0]-q[0]),2)+math.pow(math.fabs(p[1]-q[1]),2))

#Gets the height of the triangle formed by all three squares using some trig
#Can return a negative height, this is how we find the orientation of the corners
def triangleHeight(l,m,j):
	a = -((m[1] - l[1])/(m[0] - l[0]))
	b = 1.0
	c = (((m[1] - l[1])/(m[0] - l[0]))*l[0]) - l[1]
	try:
		pdist = (a*j[0]+(b*j[1])+c)/math.sqrt((a*a)+(b*b))
	except:
		return 0
	else:
		return pdist

#Gets line slope between two points
def slope(l,m):
	dx=m[0]-l[0]
	dy=m[1]-l[1]

	dxy=float(dy)/float(dx)
	return round(dxy)

#Finds the orientation of the corner squares by comparing distances between the centers
def findCornerOr(centers):
	AB=distance(centers[0],centers[1])
	BC=distance(centers[1],centers[2])
	AC=distance(centers[0],centers[2])

	#Find the outlier corner by comparing distances
	if(AB>BC and AB>AC):
		outlier = 2
		median1 = 0
		median2 = 1
	elif(AC>AB and AC>BC):
		outlier = 1
		median1 = 0
		median2 = 2
	elif(BC>AB and BC>AC):
		outlier = 0
		median1 = 1
		median2 = 2

	#Now find which corner is left, which one is right
	#Certain conditions must be met to determine the orientation of the QR code
	#We determine this using slopes between the points and height of triangle
	#formed by the corner squares
	ang=slope(centers[median1],centers[median2])
	ang2=slope(centers[median1],centers[outlier])
	height=triangleHeight(centers[median1],centers[median2],centers[outlier])

	if(ang < 0 and height < 0):
		bottom = median1
		right = median2
	elif(ang > 0 and height < 0 and ang2!=0):
		right = median1
		bottom = median2
	elif (ang>0 and height < 0 and ang2==0):
		right=median2
		bottom=median1
	elif(ang < 0 and height > 0):
		right = median1
		bottom = median2
	elif(ang > 0 and height > 0):
		bottom = median1
		right = median2
	elif ang==0:
		bottom=median1
		right=median2
		
	#Return the index of the outlier, bottom and right square
	return outlier,bottom,right

#Function returns all the points found in each of the three corner squares
#within the QRCode
def getPoints(imagePath,G1=3,G2=5):

	#We will return this array of points later
	returnArray=np.zeros((6,2),dtype=np.float32)

	#Load the image
	origImg=cv2.imread(imagePath)

	#set lower and upper bounds to filter out background
	lower=np.array([180,180,180],dtype='uint8')
	upper=np.array([255,255,255],dtype='uint8')

	#Remove anything that isnt white from image
	mask=cv2.inRange(origImg,lower,upper)
	img=cv2.bitwise_and(origImg,origImg,mask=mask)

	gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

	#Gaussian blur to find edges
	img=cv2.GaussianBlur(gray,tuple((G1,G2)),0)

	#Find edges using canny
	edges=cv2.Canny(img,10,400)

	#Get contours,hierarchy
	_,contours,hierarchy=cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	bContourArea=cv2.contourArea(contours[0])

	#Compute the center of the big contour for later
	M=cv2.moments(contours[0])
	cX=int(M["m10"]/M["m00"])
	cY=int(M["m01"]/M["m00"])

	patternCenter=tuple((cX,cY))

	#This list stores the corner contours
	cornerContours=[]

	#Get the area of the contours and get the contours that define the corner squares
	for i in range(0,len(contours)):
		area=cv2.contourArea(contours[i])

		#TODO - make this different
		if area:
			ratio=bContourArea/area
		else:
			ratio=0

		#Found a corner square if ratio between area of paper contour and square
		#lies in this range.
		if (ratio > 90) and (ratio<115):
			cornerContours.append(i)


	centers=[]
	squares=[]
	#We only need every other contour because two are returned for each corner square
	for i in cornerContours[::2]:
		#Approximate the shape of the contour to get the square points
		epsilon=0.1*cv2.arcLength(contours[i],True)
		approx=cv2.approxPolyDP(contours[i],epsilon,True)
		#Average x and y points of each box to find center of each corner square
		x=0
		y=0
		for k in range(0,4):
			x+=approx[k][0][0]
			y+=approx[k][0][1]
		centers.append(tuple((x/4,y/4)))
		squares.append(approx)

	if len(squares)<3:
		return returnArray,0

	#Find the orientation of the corner squares
	outlier,bottom,right=findCornerOr(centers)

	#We build an array of points to return :
	#Outlier outer,outlier inner, bottom outer, bottom inner, right outer, right inner
	returnArray[0],returnArray[1]=getSquarePoints(squares[outlier],patternCenter)
	returnArray[2],returnArray[3]=getSquarePoints(squares[bottom],patternCenter)
	returnArray[4],returnArray[5]=getSquarePoints(squares[right],patternCenter)
	returnArray=np.expand_dims(returnArray,axis=1)

	return returnArray,1
