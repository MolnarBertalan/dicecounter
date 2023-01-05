import os
import msvcrt
import csv
import image

def Init(chk):

    global path_in
    path_in = "***/Pictures/"

    global path_out
    path_out =  path_in + "Result.csv"

    global filelist
    filelist = [f for f in os.listdir(path_in) if f.endswith(".png")]

    global pic_count
    pic_count = len(filelist)

    global writer
    writer = csv.writer(open(path_out,'w',newline = ''))

    global header
    header = ['Picture', 'Number_of_dice', 'Results']

    if chk:
        header.insert(1,'Response')

        global response_dic
        response_dic = {
        'y':"correct",
        'd':"dot",
        'c':"clustering",   
        'b':"both"}

        global stats_dic
        stats_dic = {
        "correct":0,
        "dot":0,
        "clustering":0,   
        "both":0,
        "unknown":0}

#------------------------------------------------------------

def PrepResults(pic, dice):
    row=[d[0] for d in dice]
    row.insert(0,str(len(dice)) + 'D')
    row.insert(0,pic)
    return row


def CheckResult(res):
    print(res)
    print('Correct?, y = correct, d = dot error, c = clustering error, b = both')
    print()

    resp = response_dic.get(chr(msvcrt.getch()[0]),"unknown")
    stats_dic[resp] += 1/pic_count
    res.insert(1,resp)

    return res

#------------------------------------------------------------

print('Validate results? y/n')
chk = chr(msvcrt.getch()[0]) == 'y'

Init(chk)

print("Count_of_images: " + str(pic_count))

if chk: 
    print('Press y/d/c/b to validate result.')

print('Writing: ' + path_out) 
writer.writerow(["Count_of_images:," + str(pic_count)])
writer.writerow(header)   

    
for f in filelist:
    print('Processing: ' + f)

    dots, dice = image.Process_img(path_in+f)
    res = PrepResults(path_in+f, dice)
        
    if chk:
        image.Overlay(path_in+f, dice, dots)
        res = CheckResult(res)
        image.Close()

    writer.writerow(res)

if chk:
    for key in stats_dic:
        print(key + ': ' + str(stats_dic[key]))
        writer.writerow([key + ':,' + str(stats_dic[key])])
    










