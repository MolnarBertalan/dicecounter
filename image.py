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
params.minCircularity = 0.6

params.filterByConvexity = True
params.minConvexity = 0.8

params.filterByInertia = True
params.minInertiaRatio = 0.8

detector = cv2.SimpleBlobDetector_create(params)

SizeFactor = 1.4

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
            cv2.THRESH_BINARY_INV,9,20)

    if BW_img is None: 
        print("Error: Cannot process image")
        return -1

    return BW_img


def GetDots(BW_img):
    dots = detector.detect(BW_img)
    return dots


def Simple_cluster(dots, dice, Factor):
    if len(dots) > 0:

        clustering = cluster.DBSCAN(eps=Factor, min_samples=1).fit(dots)

        num_dice = max(clustering.labels_) + 1
        for i in range(num_dice):
            die = dots[clustering.labels_ == i]
            centroid = np.mean(die, axis=0)
            dice.append([len(die), *centroid])
    return dice


def Separating_cluster(dots, dice, Factor, criteria):
    dots_rest = []
    if len(dots) > 0:
        
        clustering = cluster.DBSCAN(eps=Factor, min_samples=1).fit(dots)

        num_dice = max(clustering.labels_) + 1
        for i in range(num_dice):
            die = dots[clustering.labels_ == i]

            if len(die) in criteria:
                centroid = np.mean(die, axis=0)
                dice.append([len(die), *centroid])
            else:
                for d in die:
                    dots_rest.append(d)

        dots_rest = np.asarray(dots_rest)
    return dice, dots_rest


def GetDice(dots):
    dots_next = []
    S = []

    for d in dots:
        if d != None:
            dots_next.append(d.pt)
            S.append(d.size)

    dist = max(S)*SizeFactor
    dots_next = np.asarray(dots_next)

    dots_6 =[]
    dots_rest = []
    dice = []

#6---------------------------------------------------------------------------------------
    if len(dots_next) > 0:        
        clustering = cluster.DBSCAN(eps=dist, min_samples=1).fit(dots_next)

        num_dice = max(clustering.labels_) + 1
        for i in range(num_dice):
            die = dots_next[clustering.labels_ == i]

            if len(die) == 3:
                for d in die:
                    dots_6.append(d)
            else:
                for d in die:
                    dots_rest.append(d)

        dots_6 = np.asarray(dots_6)
        dots_next = np.asarray(dots_rest)

        dice = Simple_cluster(dots_6, dice, dist*2)

#35-------------------------------------------------------------------------------------
    dice, dots_next =  Separating_cluster(dots_next, dice, dist*1.4, [3,5])    
#4--------------------------------------------------------------------------------------
    dice, dots_next =  Separating_cluster(dots_next, dice, dist*1.9, [4])
#rest-----------------------------------------------------------------------------------
    dice = Simple_cluster(dots_next, dice, dist*2.7)
    return dice


def Process_img(pic):
    img = OpenImage(pic)
    BW_img = PreProcess(img)

    #cv2.imshow("image",cv2.resize(BW_img,[400,700],interpolation = cv2.INTER_AREA))
    #cv2.waitKey(0)

    dots = GetDots(BW_img)
    dice = GetDice(dots)

    return dots, dice


def Overlay(pic,dice,dots):
    img = OpenImage(pic)

    for d in dots:
        pos = d.pt
        r = d.size / 2

        cv2.circle(img,                      #image
                  (int(pos[0]),int(pos[1])), #posistion
                   int(r),                   #radius
                  (0, 0, 255),               #BGR color
                   2)                        #thickness
    
    for d in dice:
        textsize = cv2.getTextSize(str(d[0]), cv2.FONT_HERSHEY_PLAIN, 6, 4)[0]
        cv2.putText(img, str(d[0]),
                    (int(d[1] - textsize[0] / 2),int(d[2] + textsize[1] / 2)),
                    cv2.FONT_HERSHEY_PLAIN, 6, (255, 150, 0), 4)

    cv2.imshow("image",cv2.resize(img,[400,700],interpolation = cv2.INTER_AREA))
    cv2.waitKey(100)


def Close():
    cv2.destroyAllWindows()
