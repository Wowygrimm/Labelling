import sys
import cv2
import pandas as pd

path = sys.argv[1]
name_pict = sys.argv[2]

# The main goal of this script is to check if the YOLO predictions are related to real objects

"""
Draw rectangles

This function draws rectangles on the picture we've chosen where the YOLO algorithm detected an objects

Args:
    dataset(dataframe): The dataframe of all the screenshots with all the items recognized

Returns:
    refPt(List): A list with the coordinates of the top-left and bottom-right corner of the rectangles that will be drawn
"""
def rect(data):
    fich = data.values
    refPt = []
    l = len(fich)
    for i in range(l):
        if (fich[i][0] == path + name_pict):
            refPt.append([(int(fich[i][1]),int(fich[i][2])),(int(fich[i][3]),int(fich[i][4]))])
    return(refPt)

"""
Main Function
"""
def main():
    refPt = []
    image = cv2.imread(path + name_pict)
    height = image.shape[0]
    width = image.shape[1]
    quotient = height/width
    clone = image.copy()
    data = pd.read_csv('dataset2.csv')
    refPt = rect(data)
    n = len(refPt)
    for i in range(n):
        cv2.rectangle(clone, refPt[i][0], refPt[i][1], (0, 255, 0), 2)
    cv2.namedWindow("image", cv2.WINDOW_KEEPRATIO)
    height_bis = min(height,1500)
    width_bis = int(height_bis/quotient)
    # This line keeps the good quotient between the height and the width of the original image
    cv2.resizeWindow("image", width_bis,height_bis)
    while True:
        cv2.imshow("image", clone)
        #This condition allows the user to quit the window and finish the program
        key = cv2.waitKey(1)
        if key == ord("q"):
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
   main()
