import cv2
import numpy as np
import glob
import QRCODE

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
# imgPoints.append(QRCODE.getPoints("markerImages/IMG_6719.JPG"))
# imgPoints.append(QRCODE.getPoints("markerImages/IMG_6720.JPG"))

objPoints.append(objp)
# print imgPoints
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, gray.shape[::-1],None,None)

print dist

dist=np.multiply(dist,0.00001)

print "ret is : "+str(ret)
print "mtx is : "+str(mtx)
print "dist is : "+str(dist)
print "rvecs are : " + str(rvecs)
print "tvecs are : " + str (tvecs)


#Now for undistortion , lets see if this worked at all
#Get height, width

img2=cv2.imread('markerImages/IMG_6719.JPG')
h,w=img2.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
print newcameramtx
print roi


dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)
x,y,w,h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite('calibresult.png',dst)
