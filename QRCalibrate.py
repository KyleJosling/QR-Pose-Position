import cv2
import numpy as np
import glob
import QRPoints

#This program calibrates the camera using the images given.

#read images
images=glob.glob('markerImages/*.JPG')

#Termination criteria
criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,30,0.001)

#Initialize 3D point array.
objp=np.zeros((6,3),dtype=np.float32)

#List of points in the pattern.png image. Coordinates correspond to cm.
#These are object points so they are three dimensional, z always being 0
pointList=[[0,0,0],[2.464,2.464,0],[0,8.8,0],[2.464,6.336,0],[8.8,0,0],[6.336,2.464,0]]

#Append the points to 3D point array
for i,x in zip(pointList,range(0,len(pointList))):
	objp[x]=i


#These lists store the points in the 2D image and the corresponding points on
#the object
imgPointsList=[]
objPointsList=[]


#QRCODE.getPoints() gets the marker points from the image.
#Append the points to the lists
for fname in images:
	print fname
	#read an image
	image=cv2.imread(fname)
	gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

	#Get the corner points
	points,success=QRPoints.getPoints(fname)

	#If the function isn't successful
	if not success:
		#Try again and add points to imgPointsList array
		points,success=QRPoints.getPoints(fname,7,3)
		cv2.cornerSubPix(gray,points,(11,11),(-1,-1),criteria)
		imgPointsList.append(points)
		objPointsList.append(objp)
	else:
		cv2.cornerSubPix(gray,points,(11,11),(-1,-1),criteria)
		imgPointsList.append(points)
		objPointsList.append(objp)

#calibrate the camera with the img points and the object points
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPointsList, imgPointsList, gray.shape[::-1],None,None)

#Write to file
np.savez('iPhoneCam2.npz',mtx=mtx,dist=dist,rvecs=rvecs,tvecs=tvecs)

#Find the projection error
mean_error = 0
for i in xrange(len(objPointsList)):
	imgpoints2, _ = cv2.projectPoints(objPointsList[i], rvecs[i], tvecs[i], mtx, dist)
	print imgpoints2.shape
	print imgPointsList[i].shape
	error = cv2.norm(imgPointsList[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
	mean_error += error
print "total error: ", mean_error/len(objPointsList)
