import cv2
import numpy as np
import glob
import math
import QRPoints

#Load npz file with camera calibration parameters
with np.load('iPhoneCam2.npz') as X:
	mtx,dist,_,_=[X[i] for i in('mtx','dist','rvecs','tvecs')]

print mtx
print dist

#Criteria
criteria=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER)

#3D point array
objectPoints=np.zeros((6,3),dtype=np.float32)

#List points in the pattern.png image. The coordinates correspond to cm
#pointList=[[0,0,0],[2.464,0,0],[2.464,2.464,0],[0,2.464,0],[6.336,0,0],[8.8,0,0],[8.8,2.464,0],[6.336,2.464,0],[0,6.336,0],[2.464,6.336,0],[2.464,8.8,0],[0,8.8,0]]
pointList=[[0,0,0],[2.464,2.464,0],[0,8.8,0],[2.464,6.336,0],[8.8,0,0],[6.336,2.464,0]]

#Axis to draw on the image later. Axis will be as long as the QRCode
axis = np.float32([[8.8,0,0], [0,8.8,0], [0,0,-8.8]]).reshape(-1,3)

#Drawing function
def draw(img,corners,imgpts):
	corner=tuple(corners[0].ravel())
	img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
	return img

#Add the points into the 3D point array
for i,x in zip(pointList,range(0,len(pointList))):
	objectPoints[x]=i



#Load the images

images=glob.glob('markerImages/*.JPG')

for fname in images:
	print "File name: " + str(fname)

	image=cv2.imread(fname)

	imagePoints,success=QRPoints.getPoints(fname)

	if not success:
		imagePoints,success=QRPoints.getPoints(fname,7,5)

	#Now use solvePnP to get the rotation and translation vectors
	ret,rvecs,tvecs=cv2.solvePnP(objectPoints,imagePoints,mtx,dist)

	#get projected points for drawing axis in image
	projectedPoints,_=cv2.projectPoints(axis,rvecs,tvecs,mtx,dist)

	#Draw our axis on the image for testing
	image=draw(image,imagePoints,projectedPoints)

	#Now get distance, angle
	rotationMat=cv2.Rodrigues(rvecs)[0]

	#Get camera position
	camPos=-np.matrix(rotationMat).T * np.matrix(tvecs)

	#create the projection matrix
	projMat=np.hstack((rotationMat,tvecs))

	#get euler angles from projection matrix
	eul=-cv2.decomposeProjectionMatrix(projMat)[6]

	yaw=eul[1,0]
	pitch=(eul[0,0]+(90))*math.cos(eul[1,0])
	roll=(-(90)-eul[0,0])*math.sin(eul[1,0]) +eul[2,0]

	#Add text
	font=cv2.FONT_HERSHEY_DUPLEX
	cv2.putText(image,("X: " + str(camPos[0][0][0])),(10,200),font,4,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(image,("Y: " + str(camPos[1][0])),(10,350),font,4,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(image,("Z: " + str(-camPos[2][0])),(10,500),font,4,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(image,("Yaw: " + str(round(yaw,2))),(10,650),font,4,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(image,("Pitch: " + str(round(pitch,2))),(10,800),font,4,(255,255,255),2,cv2.LINE_AA)
	cv2.putText(image,("Roll: " + str(round(roll,2))),(10,950),font,4,(255,255,255),2,cv2.LINE_AA)

	cv2.namedWindow('img',cv2.WINDOW_NORMAL)
	cv2.imshow('img',image)
	cv2.resizeWindow('img',600,600)
	cv2.waitKey(0)




cv2.destroyAllWindows()
