import os
import msvcrt
import csv
import cv2
import numpy as np
from sklearn import cluster

#detector params--------------------------------------

params = cv2.SimpleBlobDetector_Params()

params.minThreshold = 0
params.maxThreshold = 255

params.filterByArea = True
params.minArea = 10

params.filterByCircularity = True
params.minCircularity = 0.8

params.filterByConvexity = True
params.minConvexity = 0.87

params.filterByInertia = True
params.minInertiaRatio = 0.8

detector = cv2.SimpleBlobDetector_create(params)

SizeFactor = 3.8

#Prep files-------------------------------------------

path_in = "***/Pictures/"
path_out =  path_in + "Result.csv"
path_comp = path_in + "Compare.csv"

filelist=os.listdir(path_in)

Res = open(path_out,'w',newline = '')
writer_R = csv.writer(Res)

header = ['Picture', 'Number of dice', 'Results:']
writer_R.writerow(header)

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

def GetDice(dots,Factor):

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

    S_corr = max(S)

    if len(X) > 0:
        dice = []
        clustering = cluster.DBSCAN(eps=S_corr*Factor, min_samples=1).fit(X)

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
    row.insert(0,str(len(dice)) + 'D')
    row.insert(0,pic)
    writer_R.writerow(row)
    return row
def PrintCheck(res):
    print('Correct? y/n')
    chk = chr(msvcrt.getch()[0]) == 'y'
    res.insert(1,chk)
    writer_comp.writerow(res)
    
def Process_img(pic, chk,Factor):
    img = OpenImage(pic)
    BW_img = PreProcess(img)
    dots = GetDots(BW_img)
    dice = GetDice(dots,Factor)
    
    res = PrintResults(pic, dice)

    if chk:
        print(res)
        Overlay(img, dice, dots)
        PrintCheck(res)

#-----------------------------------------------------

print('Check Results, and compare? y/n')
chk = chr(msvcrt.getch()[0]) == 'y'

if chk:
    print('Writing: ' + path_out)
    print('1. Select window with picture.') 
    print('2. Press any button to close picture.')
    print('3. Press y/n to validate result.')

    comp = open(path_comp,'w',newline = '')
    writer_comp = csv.writer(comp)
    
    header.insert(1,'Correct?')
    writer_comp.writerow(header)

for f in filelist:
    if (f.endswith(".png")):
        print('Processing: ' + f)
        Process_img(path_in+f, chk, SizeFactor)














