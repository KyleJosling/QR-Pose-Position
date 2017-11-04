import cv2
import numpy as np
import glob
import QRCODE


def draw(img,corners,imgpts):
	corner=tuple(corners[0].ravel())
	img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
	return img


img=cv2.imread("markerImages/IMG_6727.JPG")
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#Termination criteria
critera=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER)

#Initialize 3D point array.
objp=np.zeros((12,3),dtype=np.float32)
#List of points in the pattern.png image. Coordinates correspond to cm.
pointList=[[0,0,0],[2.464,0,0],[2.464,2.464,0],[0,2.464,0],[6.336,0,0],[8.8,0,0],[8.8,2.464,0],[6.336,2.464,0],[0,6.336,0],[2.464,6.336,0],[2.464,8.8,0],[0,8.8,0]]
#Append the points to 3D point array
for i,x in zip(pointList,range(0,len(pointList))):
	objp[x]=i

imgPoints=[]
objPoints=[]
#Use this function to get the marker points from the current image.
#Append the points to the list
imgPoints.append(QRCODE.getPoints("markerImages/IMG_6727.JPG"))
#imgPoints.append(QRCODE.getPoints("markerImages/TEST.JPG"))
imgPoints.append(QRCODE.getPoints("markerImages/IMG_6720.JPG"))
objPoints.append(objp)
#objPoints.append(objp)
objPoints.append(objp)
# print imgPoints
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, gray.shape[::-1],None,None)

# print dist

#dist=np.multiply(dist,0.00001)

# print "ret is : "+str(ret)
# print "mtx is : "+str(mtx)
# print "dist is : "+str(dist)
# print "rvecs are : " + str(rvecs)
# print "tvecs are : " + str (tvecs)


#Now for undistortion , lets see if this worked at all
#Get height, width

img2=cv2.imread('markerImages/IMG_6720.JPG')
h,w=img2.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
# print newcameramtx
# print roi


dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png',dst)

mean_error = 0
for i in xrange(len(objPoints)):
	imgpoints2, _ = cv2.projectPoints(objPoints[i], rvecs[i], tvecs[i], mtx, dist)
	error = cv2.norm(imgPoints[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
	mean_error += error
img4=cv2.imread("markerImages/IMG_6719.JPG")
print "total error: ", mean_error/len(objPoints)

#okay now lets draw the axis
axis = np.float32([[8.8,0,0], [0,8.8,0], [0,0,-8.8]]).reshape(-1,3)
corners2=QRCODE.getPoints("markerImages/IMG_6719.JPG")
_,rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, corners2, mtx, dist)
imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)
img3 = draw(img4,corners2,imgpts)
cv2.namedWindow('img',cv2.WINDOW_NORMAL)
cv2.imshow('img',img3)
cv2.resizeWindow('img', 600,600)
cv2.waitKey(0)
cv2.destroyAllWindows()
