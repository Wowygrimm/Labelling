# -*- coding: utf-8 -*-
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
import argparse

path2 = sys.argv[1]      #Exemples path2 = "data/01net/"
name_pict = sys.argv[2]           #nom = "01net"

"""
Cutting Function

This function divides the original screenshot into smaller pictures, taking into account the original size of the screenshot :
if the sreenshot is big, there will be more images at the end.

Args:
    image (numpy.array): The original screenshot that will be cut
    name (str): the name of the website

Returns:
    (h, a): h is the cutting step while a is the number of images created.
"""
def cut(image,name):
    width = image.shape[1]
    height = image.shape[0]
    if height > 6408 :
        a = 8
        h = height//a
    else :
        a = 4
        h = height//4
    for i in range(a):
            img = name+str(i)+'.png'
            cv2.imwrite(path2 + img,image[i*h:(i+1)*h,:])
    return(h,a)

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
    for i in range(len(fich)):
        if (fich[i][0] == ' ' + path2 + name_pict + str(j) + '.png'):
            k = k+1
            j = j+1
            if (fich[i][3] != fich[i][5]):
                fich[i][3] = fich[i][3] + h*k
                fich[i][5] = fich[i][5] + h*k
        else:
            if (fich[i][3] != fich[i][5]):
                fich[i][3] = fich[i][3] + h*k
                fich[i][5] = fich[i][5] + h*k
    return(pd.DataFrame(data = fich[:,:],
                        columns = ['Photo','Objet','Left','Top','Right','Bottom']))

"""
Main Function

This function does the cutting of the screenshot, uses YOLO to detect objects, then stores everything into a dataframe
"""

def main():
    dataset = pd.read_csv("dataset.csv", index_col = None)
    im = cv2.imread(path2 + name_pict + '.png')
    (h,n) = cut(im,name_pict) # im is the image we'd like to cut, name_pict is a string containing the future pictures' name
                        # h is the height of a fragmented picture and n is the number of fragmented pictures
    process = subprocess.Popen("darknet.exe detect cfg/yolov3.cfg yolov3.weights " + path2 + name_pict + "0.png > base2.txt", shell=True, stdout=subprocess.PIPE)
    process.wait()
    for i in range(1,n):
        print(i)
        process = subprocess.Popen("darknet.exe detect cfg/yolov3.cfg yolov3.weights " + path2 + name_pict +str(i) + '.png' ">> base2.txt", shell=True, stdout=subprocess.PIPE)
        process.wait()
    col = ['Photo', 'Object', 'Left', 'Top', 'Right', 'Bottom']
    raw_data = pd.read_csv("base2.txt", sep=',', header = None, index_col = None)
    raw_data.columns = col
    datac = conc(raw_data,h)
    dataset2 = dataset.append(datac)
    dataset2.to_csv('dataset.csv', index = False)

if __name__ == '__main__':
   main()
#At this point, change the picture 'im' and execute the 'main' function once again.
