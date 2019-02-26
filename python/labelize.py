# import the necessary packages
import argparse
import cv2
import pandas as pd
import numpy as np
import os
import sys
from tkinter import *

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
coords = []
offset = []
cropping = False
selecting = False
redit = False # When an image/csv is load again to edit
label = ""

"""
First operator (Click and crop/Zoom)

This function allows the user to do 2 things : if he uses the left mouse button,
he draws as many rectangles on the screenshot as he wants then the coordinates
are stored in a dataset at the end of the operationself.
If he uses the right button, he can zoom on the region he
chooses to zoom on and then draw rectangles on them. He can also do bothself.

Args:
	Global variables : coords	- Where the coordinates are going to be stored
					   cropping - A variable indicating if the user still presses the button
					   offset	- A list where the coordinates of the new window are store

Returns:
	Nothing - The function ends with an action of the user

"""

class InputApp(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		
		self.root = Tk()
		self.root.title('Integration of label coordinates')
		self.root.geometry('500x100')
		
		self.pack()
		self.output()

	def output(self):
		self.labelBox = Label(self.root, text='Label:')
		self.labelBox.pack(side=LEFT, padx=5, pady=5)

		self.inputBox = Entry(self.root, width=10)
		self.inputBox.pack(side=LEFT ,padx=5, pady=5)
		
		self.submitButton = Button(self.root, text='Submit', command=self.saveLabel)
		self.submitButton.pack(side=RIGHT, padx=5, pady=5)

		self.root.bind("<Return>", self.saveLabel)

	def saveLabel(self, event=None):
		global label
		label = self.inputBox.get()

		self.root.quit()
		self.root.destroy()
		self.__init__()

	def start(self):
		self.root.after(1, lambda: self.root.focus_force())
		self.inputBox.focus()
		self.root.mainloop()



def select_area_box(event, x, y, flags, param):
	# grab references to the global variables
	global coords, cropping, selecting, temp_img, roi

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that selection is being
	# performed
	if(event == cv2.EVENT_LBUTTONDOWN):
		coords = [(x, y)]
		selecting = True
	# check to see if the left mouse button was released
	elif(event == cv2.EVENT_LBUTTONUP):
		# Update actual coordinates
		if(len(coords) == 2):
			coords[1] = (x, y)
		else:
			coords.append((x, y))

		# End the selection
		selecting = False

		# If cropping inprocess, select roi image
		if(cropping):
			temp_img = roi.copy()
		else:
			temp_img = img_resized.copy()

		# draw a rectangle around the region of interest
		cv2.rectangle(temp_img, coords[0], coords[1], (255, 0, 0), 2)
		cv2.imshow("image", temp_img)
	# Check if the mouse is beeing moved and selection is being performed
	elif(event == cv2.EVENT_MOUSEMOVE):
		if(selecting):
			# Update actual coordinates
			if(len(coords) == 2):
				coords[1] = (x, y)
			else:
				coords.append((x, y))

			# If cropping inprocess, select roi image
			if(cropping):
				temp_img = roi.copy()
			else:
				temp_img = img_resized.copy()

			cv2.rectangle(temp_img, coords[0], coords[1], (255, 0, 0), 2)
			cv2.imshow("image", temp_img)

"""
Main function
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Label areas of an given image")
	parser.add_argument("-i", "--image",	required=True,	help="Path to the image")
	parser.add_argument("-f", "--file",		required=False, help="Path to .csv file", default="data_labeled.csv")
	args = parser.parse_args()

	# If .csv file exists we load it
	if(os.path.exists(args.file)):
		dataset = pd.read_csv(args.file, index_col = None)
	# else we create a dataframe object
	else:
		dataset = pd.DataFrame(data = [], columns = ['Photo','Left','Top','Right','Bottom', 'Label'])

	if(not os.path.exists(args.image)):
		raise FileNotFoundError(args.image)

	# Load the image
	image = cv2.imread(args.image)
	# fich = []
	img_height = image.shape[0]
	img_width = image.shape[1]
	img_ratio = img_height / img_width
	img_new_height = min(img_height, 800)
	img_new_width = int(img_new_height/img_ratio)

	# Create text input window
	inputWindow = InputApp()

	# Create editing window
	cv2.namedWindow("image", cv2.WINDOW_AUTOSIZE)

	# Resize image
	img_resized = cv2.resize(image, (img_new_width, img_new_height))
	scale = image.shape[0] / img_new_height

	# Display image
	cv2.imshow("image", img_resized)
	clone = img_resized.copy()
	previous_img_state = img_resized.copy()
	temp_img = None
	cv2.setMouseCallback("image", select_area_box)

	# Display previously saved Label items from csv file
	for row in dataset.iterrows():
		redit = True # Previous data found
		cv2.rectangle(img_resized, (int(row[1]["Left"]/scale), int(row[1]["Top"]/scale)), (int(row[1]["Right"]/scale), int(row[1]["Bottom"]/scale)), (0, 255, 0), 3)


	# keep looping until the 'q' key is pressed
	while True:
		# display the image and wait for a keypress
		key = cv2.waitKey(1) & 0xFF

		# if the 'r' key is pressed, reset the cropping region
		if(key == ord("r")):
			print("Reseting image")
			cropping = False
			img_resized = clone.copy()
			dataset = pd.DataFrame(data = [], columns = ['Photo','Left','Top','Right','Bottom', 'Label'])
			cv2.imshow("image", img_resized)
		elif(key == ord("p")):
			print("Going back to previous change")
			if(not cropping):
				img_resized = previous_img_state.copy()

				if(redit):
					redit = False
					dataset = pd.DataFrame(data = [], columns = ['Photo','Left','Top','Right','Bottom', 'Label'])
				else:
					dataset.drop(dataset.tail(1).index, inplace=True)

			cropping = False
			cv2.imshow("image", img_resized)

		elif(key == ord("l")):
			if(temp_img is not None):
				print("Labelizing")
				if(cropping):
					temp_img = img_resized.copy()

					coords[0] = (offset[0] + int(coords[0][0]/scale), offset[1] + int(coords[0][1]/scale))
					coords[1] = (offset[0] + int(coords[1][0]/scale), offset[1] + int(coords[1][1]/scale))
					cropping = False

				cv2.rectangle(temp_img, coords[0], coords[1], (0, 255, 0), 2)
				previous_img_state = img_resized.copy()
				img_resized = temp_img.copy()
				
				inputWindow.start()

				dataset = dataset.append([{
					"Photo": args.image,
					"Left": coords[0][0]*scale,
					"Top": coords[0][1]*scale,
					"Right": coords[1][0]*scale,
					"Bottom": coords[1][1]*scale,
					"Label": label
				}])

				cv2.imshow("image", img_resized)
		elif(key == ord("c")):
			if(not cropping):
				roi = image[int(coords[0][1]*scale):int(coords[1][1]*scale), int(coords[0][0]*scale):int(coords[1][0]*scale)]

				cv2.imshow("image", roi)
				offset = coords[0]
				cropping = True
		# if the 'q' key is pressed, break from the loop
		elif(key == ord("q")):
			break
		elif(key == ord("s")):
			# Export image
			for row in dataset.iterrows():
				cv2.rectangle(image, (int(row[1]["Left"]), int(row[1]["Top"])), (int(row[1]["Right"]), int(row[1]["Bottom"])), (0, 255, 0), 3)

			_, file_extension = os.path.splitext(args.image)
			new_filename = args.image.replace(file_extension, "_export"+file_extension)
			print("Exporting image to "+new_filename)
			cv2.imwrite(new_filename, image)

			print("Exporting objects to "+args.file)
			dataset.to_csv(args.file, index = False)
			break

	# close all open windows
	cv2.destroyAllWindows()
