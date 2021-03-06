# QR-Pose-Position
<h2> Option 1 </h2>

This zip file https://www.dropbox.com/s/g67dmolq79ko4jk/Camera%20Localization.zip?dl=0 contains a number of images taken from different positions and orientations with an iPhone 6. Each image is the view of a pattern on a flat surface. The original pattern that was photographed is 8.8cm x 8.8cm and is included in the zip file. Write a Python program that will visualize (i.e. generate a graphic) where the camera was when each image was taken and how it was posed, relative to the pattern.

You can assume that the pattern is at 0,0,0 in some global coordinate system and are thus looking for the x, y, z and yaw, pitch, roll of the camera that took each image. Please submit a link to a Github repository contain the code for your solution. Readability and comments are taken into account too. You may use 3rd party libraries like OpenCV and Numpy.

<h2> Approach </h2>

<h3> QRPoints.py </h3>

QRPoints gets points on the corners of the three squares in the QR Code. The technique is as follows:

1. Filter out any points that aren't white
2. Detect contours, find the squares in the QR Code by comparing contour areas
3. Get orientation of squares by comparing distances and slopes
4. Return image points of corners of squares in a predefined order

<h3> Calibration (QRCalibrate.py) </h3>

1. QRPoints.py gets certain image points on the QR Code 
2. Used image points to calibrate the camera with a set of corresponding object points, that are predefined based on the size of the pattern
3. Use calibrate camera with object points and image points
4. Saved calibration parameters as npz file

<h3> Getting Pose and Position (visualize.py) </h3>

1. Load calibration parameters
2. Find image points in QR Code using QRPoints.py, use solvePnP to get rotation vectors
3. Draw axes on image, each axis being 8.8cm long
4. Get rotation matrix from rotation vectors using cv2.Rodrigues()
5. Decompose rotation matrix into yaw, pitch and roll angles

Yaw, pitch and roll follow the aircraft principle axes and the right hand rule. Also please note that the blue axis is the x axis, green is the y axis and red is the z axis. The x,y,z coordinates are in cm. 

