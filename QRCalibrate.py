import cv2
import numpy as np
import glob
import QRCODE

#Function to draw axis
def draw(img,corners,imgpts):
	corner=tuple(corners[0].ravel())
	img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
	return img

images=glob.glob('testImages/*.JPG')

#Termination criteria
critera=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER)

#read img
img=cv2.imread("markerImages/IMG_6727.JPG")
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#Initialize 3D point array.
objp=np.zeros((12,3),dtype=np.float32)
#List of points in the pattern.png image. Coordinates correspond to cm.
pointList=[[0,0,0],[2.464,0,0],[2.464,2.464,0],[0,2.464,0],[6.336,0,0],[8.8,0,0],[8.8,2.464,0],[6.336,2.464,0],[0,6.336,0],[2.464,6.336,0],[2.464,8.8,0],[0,8.8,0]]
#Append the points to 3D point array
for i,x in zip(pointList,range(0,len(pointList))):
	objp[x]=i


imgPoints=[]
objPoints=[]


#QRCODE.getPoints() gets the marker points from the image.
#Append the points to the lists
#TODO- make a hash table with each image and the corresponding array points
#So you don't have to recalculate them
for fname in images:
	print fname
	#read an image
	image=cv2.imread(fname)

	#set lower and upper bounds to filter out background
	lower=np.array([180,180,180],dtype='uint8')
	upper=np.array([255,255,255],dtype='uint8')

	#Remove anything that isnt white from image.
	mask=cv2.inRange(image,lower,upper)
	output=cv2.bitwise_and(image,image,mask=mask)

	#TODO-make it so you don't have to write the image before sending it to getPoints
	cv2.imwrite('whiteOnly.JPG',output)

	#Get the corner points
	points,success=QRCODE.getPoints('whiteOnly.JPG')

	#TODO- fix the detector so it works with all the images. seriously

	#If the function isn't successful
	if not success or fname=='testImages/IMG_6723.JPG':
		#Try again and add points to imgPoints array
		points,success=QRCODE.getPoints('whiteOnly.JPG',7,3)
		imgPoints.append(points)
		objPoints.append(objp)
	else:
		imgPoints.append(points)
		objPoints.append(objp)

#calibrate the camera with the img points and the object points
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, gray.shape[::-1],None,None)

img2=cv2.imread('markerImages/IMG_6719.JPG')
h,w=img2.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png',dst)

mean_error = 0
for i in xrange(len(objPoints)):
	imgpoints2, _ = cv2.projectPoints(objPoints[i], rvecs[i], tvecs[i], mtx, dist)
	error = cv2.norm(imgPoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
	mean_error += error
print "total error: ", mean_error/len(objPoints)

#okay now lets draw the axis
axis = np.float32([[8.8,0,0], [0,8.8,0], [0,0,-8.8]]).reshape(-1,3)
corners2,meep=QRCODE.getPoints('markerImages/IMG_6719.JPG')
print corners2

#getn rotation/translation vectors
_,rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)

#draw the image
img3 = draw(img2,corners2,imgpts)

#display image
cv2.namedWindow('img',cv2.WINDOW_NORMAL)
cv2.imshow('img',img3)
cv2.resizeWindow('img', 600,600)
cv2.waitKey(0)
cv2.destroyAllWindows()
