"""
Created on Thu Apr 26 10:43:24 2018

@author: SublimeAdmin
"""
import numpy as np
from matplotlib import pyplot as plt
import cv2
import pandas as pd
import subprocess
import sys

os_ = sys.argv[1]            #mac or win
path2 = sys.argv[2]      #Exemples path2 = "data/01net/"
name_pict = sys.argv[3]           #nom = "01net"

"""
Cutting Function

This function divides the original screenshot into smaller pictures, using the principle of sliding windows

Args:
    image (numpy.array): The original screenshot that will be cut
    name (str): the name of the website

Results:
    j+1 (int): The number of images created
"""
def cut(image,name,h):
    height = image.shape[0]
    i = 0
    j = 0
    while (h*(1+i) < height) & ((h*(1+i)+h//2) < height):
        img = name+str(j)+'.png'
        img2 = name+str(j+1)+'.png'
        cv2.imwrite(path2 + img,image[i*h:(i+1)*h,:])
        cv2.imwrite(path2 + img2,image[h//2 + i*h:(i+1)*h + h//2,:])
        i = i + 1
        j = j + 2
    img = name+str(j)+'.png'
    cv2.imwrite(path2 + img,image[i*h:,:])
    return(j+1)

"""
Fill names

This function completes the column 'Photo', if needed

Args:
    data(dataframe): A dataframe with sometimes missing information about the origin of the item recognized

Returns:
    data(dataframe): A dataframe with the column 'Photo' complete
"""

def fill(data):
    fich = data.values
    l = len(fich)
    for i in range(l):
        if (pd.isnull(fich[i][0])):
            fich[i][0] = fich[i-1][0]
    return(pd.DataFrame(data = fich[:,:],
                        columns = ['Photo','Object','Left','Top','Right','Bottom']))
"""
Boxes' real coordinates

This function gives the real coordinates of all the items recognised on a screenshot: Before this function, these coordinates are relatives to the smaller pictures

Args:
    data (dataframe): The dataframe in which all the (wrong) boxes' coordinates are stored
    step (int): The height (in pixels) of the smaller pictures

Returns:
    A dataframe with the correct coordinates
"""
def conc(data,step):
    fich = data.values
    k = -1
    h = step
    j = 0
    if (os_ == 'win'):
        for i in range(len(fich)):
            if (fich[i][0] == ' ' + path2 + name_pict + str(j) + '.png'):
                k = k+1
                j = j+1
                fich[i][0] = path2 + name_pict + '.png'
                if (fich[i][3] != fich[i][5]):
                    fich[i][3] = fich[i][3] + (h*k)//2
                    fich[i][5] = fich[i][5] + (h*k)//2
            else:
                if (fich[i][3] != fich[i][5]):
                    fich[i][3] = fich[i][3] + (h*k)//2
                    fich[i][5] = fich[i][5] + (h*k)//2
    if (os_ == 'mac'):
        for i in range(len(fich)):
            if (fich[i][0] == path2 + name_pict + str(j) + '.png'):
                k = k+1
                j = j+1
                fich[i][0] = path2 + name_pict + '.png'
                if (fich[i][3] != fich[i][5]):
                    fich[i][3] = fich[i][3] + (h*k)//2
                    fich[i][5] = fich[i][5] + (h*k)//2
            else:
                if (fich[i][3] != fich[i][5]):
                    fich[i][3] = fich[i][3] + (h*k)//2
                    fich[i][5] = fich[i][5] + (h*k)//2
    return(pd.DataFrame(data = fich[:,:],
                        columns = ['Photo','Object','Left','Top','Right','Bottom']))
"""
Dopplegangers' eraser

This function deletes all the dopplegangers: the possible items that were recognised twice

Args:
    datac (dataframe): The dataframe we obtain before the concatenation

Returns:
    datac2 (dataframe): The same dataframe but without dopplegangers
"""
def dopple_out(data):
    fich = data.values
    to_del = []
    l = len(fich)
    (e_l,e_t,e_r,e_b) = (0,0,0,0)
    for i in range(l-1):
        if (type(fich[i][2]) == float) & (type(fich[i+1][2]) == float):
            (e_l,e_t,e_r,e_b) = (abs(fich[i+1][2]-fich[i][2]),
                                abs(fich[i+1][3]-fich[i][3]),
                                abs(fich[i+1][4]-fich[i][4]),
                                abs(fich[i+1][5]-fich[i][5]))
            e = (e_l+e_t+e_r+e_b)/4
            if e < 10:
                to_del.append(i+1)
    if (to_del != []):
        fich = np.delete(fich, to_del, 0)
    return(pd.DataFrame(data = fich[:,:],
                        columns = ['Photo','Object','Left','Top','Right','Bottom']))

"""
Empty row eraser

This function deletes all the row that are empty

Args:
    datac3(dataframe): A dataframe with possible rows that have no pictures registered on

Returns:
    datac4(dataframe): A dataframe with no "empty" rows
"""

def null_out(data):
    data = data.dropna(axis = 0)
    return(data)

"""
Main Function

This function does the cutting of the screenshot, uses YOLO to detect objects, then stores everything into a dataframe
"""

def main():
    test = True
    try:
        pd.read_csv('dataset.csv')
    except FileNotFoundError:
        test = False
    if (test == False):
        data = pd.DataFrame(data = [], columns = ['Photo','Object','Left','Top','Right','Bottom'])
        data.to_csv("dataset.csv", index = False)
    dataset = pd.read_csv("dataset.csv", index_col = None)
    im = cv2.imread(path2 + name_pict + '.png')
    h = 1080
    n = cut(im,name_pict,h) # im is the image we'd like to cut, name_pict is a string containing the future pictures' name
                            # h is the height of a fragmented picture and n is the number of fragmented pictures
    base = pd.DataFrame(data = [], columns = ['Photo','Object','Left','Top','Right','Bottom'])
    base.to_csv("base.csv", index = False)
    if (os_ == 'win'):
        for i in range(n):
            print(i)
            process = subprocess.Popen("darknet.exe detect cfg/yolov3.cfg yolov3.weights " + path2 + name_pict +str(i) + '.png >> base.csv', shell=True, stdout=subprocess.PIPE)
            process.wait()
    if (os_ == 'mac'):
        for i in range(n):
            print(i)
            process = subprocess.Popen("./darknet detect cfg/yolov3.cfg yolov3.weights " + path2 + name_pict +str(i) + '.png >> base.csv', shell=True, stdout=subprocess.PIPE)
            process.wait()
    raw_data = pd.read_csv("base.csv", sep=',', index_col = None)
    datac = conc(raw_data,h)
    datac2 = fill(datac)
    datac3 = dopple_out(datac2)
    datac4 = null_out(datac3)
    dataset2 = dataset.append(datac4)
    dataset2.to_csv('dataset.csv', index = False)

if __name__ == '__main__':
   main()
#At this point, change the picture 'im' and execute the 'main' function once again.
