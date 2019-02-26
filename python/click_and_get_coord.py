# import the necessary packages
import argparse
import numpy as np
import cv2
import pandas as pd


# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
refPt_z = []
cropping = False

"""
First operator (Click and cropp/Zoom)

This function allows the user to do 2 things : if he uses the left mouse button, he draws as many rectangles on the screenshot as he wants then the coordinates are stored in a dataset at the end of the operationself.
If he uses the right button, he can zoom on the region he chooses to zoom on and then draw rectangles on them. He can also do bothself.

Args:
	Global variables : refPt - Where the coordinates are gonna be stored
					   cropping - A variable indicating if the user still presses the button
					   refPt_z - A list where the coordinates of the new window are store

Returns:
	Nothing - The function ends with an action of the user

"""
def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping, refPt_z

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True

	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False

		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", image)
		#stores the coordinates into an array
		fich.append([args["image"],refPt[0][0], refPt[0][1], refPt[1][0], refPt[1][1]])

	if event == cv2.EVENT_RBUTTONDOWN: #same but with the right mouse button instead of the left one
		refPt_z = [(x,y)]
		cropping = True

	elif event == cv2.EVENT_RBUTTONUP:
		refPt_z.append((x,y))
		cropping = False
		cv2.rectangle(image, refPt_z[0], refPt_z[1], (255, 0, 0), 2)
		cv2.imshow("image", image)

"""
Second operator (Click and capture)

This function allows the user to do 2 things : He uses the left mouse button to draw as many rectangles on the screenshot as he wants then the coordinates are stored in a dataset at the end of the operationself.
The rectangles are also drawn on the original picture


Args:
	Global variables : refPt - Where the coordinates are gonna be stored
					   cropping - A variable indicating if the user still presses the button

Returns:
	Nothing - The function ends with an action of the user

"""

def click_and_crop_2(event, x, y, flags, param):
	global refPt, cropping

	# same as before but on the new window
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True

	elif event == cv2.EVENT_LBUTTONUP:

		refPt.append((x, y))
		cropping = False

		# draw a rectangle around the region of interest, then draws the same rectangle on the original picture
		cv2.rectangle(zoom_roi, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.rectangle(image, (int(refPt[0][0]/scale)+refPt_z[0][0], int(refPt[0][1]/scale)+refPt_z[0][1]), (int(refPt[1][0]/scale)+refPt_z[0][0],int(refPt[1][1]/scale)+refPt_z[0][1]), (0, 255, 0), 2)
		cv2.imshow("ROI", zoom_roi)
		cv2.imshow("image", image)
		# stores the coordinates
		fich.append([args["image"],int(refPt[0][0]/scale)+refPt_z[0][0], int(refPt[0][1]/scale)+refPt_z[0][1], int(refPt[1][0]/scale)+refPt_z[0][0],int(refPt[1][1]/scale)+refPt_z[0][1]])

"""
Main function
"""

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to the image")
args = vars(ap.parse_args())

test = True
try:
	pd.read_csv('dataset2.csv')
except FileNotFoundError:
	test = False
if (test == False):
	data = pd.DataFrame(data = [], columns = ['Photo','Left','Top','Right','Bottom'])
	data.to_csv("dataset2.csv", index = False)
dataset = pd.read_csv("dataset2.csv", index_col = None)
# load the image, clone it, and setup the mouse callback function
fich = []
image = cv2.imread(args["image"])
clone = image.copy()
height = image.shape[0]
width = image.shape[1]
quotient = height/width
cv2.namedWindow("image", cv2.WINDOW_KEEPRATIO)
height_bis = min(height,1500)
width_bis = int(height_bis/quotient)
cv2.resizeWindow("image", width_bis,height_bis)
cv2.setMouseCallback("image", click_and_crop)

# keep looping until the 'q' key is pressed
while True:
	# display the image and wait for a keypress
	cv2.imshow("image", image)
	key = cv2.waitKey(1) & 0xFF

	# if the 'r' key is pressed, reset the cropping region
	if key == ord("r"):
		image = clone.copy()

	# if the 'q' key is pressed, break from the loop
	elif key == ord("q"):
		break

 #if there are two reference points, then crop the region of interest
 #from the image and display it
if len(refPt_z) == 2:
	height1 = refPt_z[1][1] - refPt_z[0][1]
	height_bis2 = max(height1,400)
	scale = height_bis2/height1
	roi = clone[refPt_z[0][1]:refPt_z[1][1], refPt_z[0][0]:refPt_z[1][0]]
	zoom_roi = cv2.resize(roi, (0,0), fx=scale, fy=scale)
	cv2.imshow("ROI", zoom_roi)
	cv2.setMouseCallback("ROI", click_and_crop_2)
	cv2.waitKey(0)

cv2.setMouseCallback("image", click_and_crop)

if (refPt != []):
	#Let's now store everything into a dataframe
	fich = np.asarray(fich, dtype = object)
	data = pd.DataFrame(data = fich[:,:],
						columns = ['Photo','Left','Top','Right','Bottom'])
	dataset2 = dataset.append(data)
	dataset2.to_csv('dataset2.csv', index = False)

# close all open windows
cv2.destroyAllWindows()
