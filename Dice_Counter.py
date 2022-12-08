import os
import msvcrt
import time
import csv
import cv2
import numpy as np
from sklearn import cluster

#detector params--------------------------------------

params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 0
params.maxThreshold = 255

#params.filterByArea = True
#params.minArea = 25

params.filterByCircularity = True
params.minCircularity = 0.8

params.filterByConvexity = True
params.minConvexity = 0.87

params.filterByInertia = True
params.minInertiaRatio = 0.8

detector = cv2.SimpleBlobDetector_create(params)

m = 3.8

#Prep files-------------------------------------------

path_in = "C://Users/acer/Pictures/Pictures/"
path_out =  "C://Users/acer/Pictures/Pictures/file.csv"

filelist=os.listdir(path_in)
org = open("C://Users/acer/Pictures/Pictures/org.csv",'w',newline = '')
writer_org = csv.writer(org)

fil = open(path_out,'w',newline = '')
writer_f = csv.writer(fil)

header = ['Picture', 'Number of dice', 'Results:']
writer_f.writerow(header)

#-----------------------------------------------------

def OpenImage(path):
    img = cv2.imread(path,1)
    if img is None: 
        print("Error: Cannot read image: ", path)
        return -1
    return img

def PreProcess(img):
    Gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    BW_img = cv2.adaptiveThreshold(Gray_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY_INV,7,20)
    if BW_img is None: 
        print("Error: Cannot process image")
        return -1
    return BW_img

def GetDots(BW_img):
    dots = detector.detect(BW_img)
    return dots

def GetDice(dots,m):

    X = []
    S = []
    for d in dots:
        pos = d.pt
        siz = d.size
        if d != None:
            X.append(pos)
            S.append(siz)
    X = np.asarray(X)
    S = np.asarray(S)

    S_fact = max(S)

    if len(X) > 0:
        dice = []
        clustering = cluster.DBSCAN(eps=S_fact*m, min_samples=1).fit(X)

        num_dice = max(clustering.labels_) + 1
        for i in range(num_dice):
            die = X[clustering.labels_ == i]
            centroid = np.mean(die, axis=0)
            dice.append([len(die), *centroid])

        return dice
    else:
        return []

def Overlay(img,dice,dots):
    for d in dots:
        pos = d.pt
        r = d.size / 2

        cv2.circle(img,                      #image
                  (int(pos[0]),int(pos[1])), #posistion
                   int(r),                   #radius
                  (0, 0, 255),               #BGR color
                   2)                        #thickness
    for d in dice:

        textsize = cv2.getTextSize(str(d[0]), cv2.FONT_HERSHEY_PLAIN, 3, 2)[0]

        cv2.putText(img, str(d[0]),
                    (int(d[1] - textsize[0] / 2),int(d[2] + textsize[1] / 2)),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 4)
    cv2.imshow("image",cv2.resize(img,[400,700],interpolation = cv2.INTER_AREA))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def PrintResults(pic, dice):
    row=[d[0] for d in dice]
    row.insert(0,len(dice))
    row.insert(0,pic)
    writer_f.writerow(row)
    return row

def Process_img(pic, chk,m):
    img = OpenImage(pic)
    BW_img = PreProcess(img)
    dots = GetDots(BW_img)
    dice = GetDice(dots,m)

    res = PrintResults(pic, dice)

    if chk:
        print(res)
        Overlay(img, dice, dots)

        CheckRes(res)

def CheckRes(res):
    print('Correct? y/n')
    chk = chr(msvcrt.getch()[0]) == 'y'
    res.insert(1,chk)
    writer_org.writerow(res)

#-----------------------------------------------------

print('Write Original info? y/n')
chk = chr(msvcrt.getch()[0]) == 'y'

if chk:
    print('Writing: ' + path_out)
    writer_org.writerow(header)

for f in filelist:
    if (f.endswith(".png")):
        print('Processing: ' + f)
        Process_img(path_in+f, chk, m)














