# Dobókocka felismerés

A program célja klasszikus 6 oldalú dobókockákról készült képen a pöttyök felismerése, és az egyes kockák elkülönítése.

Az alább ismertetett algoritmust a repositroyban megtalálható 109 képen teszteltem amelyek kölünböző helyzetű, darabszámú kockákról készültek, eltérő hátterek előtt és különböző nagyításban.
Az eredményt csv fájlokban rögzítettem. Result_True a 100% ban pontos (természetesen emberi) eredményt tartalmazza összehasonlítás érdekében.

A tesztet két módszerrel is elvégeztem, az egyik a pontok egyszerű clustereléssel való csoportosítását végzi. Ennek eredményei a Result_simple fájlban látható.

Később az algoritmust "lépcsős" clustereléssel egészítettem ki, amely fokozatosan növeli a pontok között megengedett távolságot. Ezzel a módszerrrel előbb elkülöníthetőek a 6-os, majd 3-as és 5-ös, 4-es és végül a 2-es 1-es kockák (pontok távolsága alapján). Ennek eredménye a Result_Complex fájl mutatja be.

A feltöltött forráskód csak a "lépcsős" módszert tartalmazza de igen egyszerűen átalakítható az egyszerű működésre.

### 1. Inicializálás

Induláskor a felhasználó választhat, hogy szeretné-e futás közben, képenként ellenőrizni az algoritmus eredményét.

A választól a program több funkciója is függ, ugyanis ha nem, akkor nincs szükség az eredmény megjelítésére és annak ellenőrzésére sem (statisztikák sem készülnek). Ilyenkor elég csak a pöttyök felismerését és a clusterezést elvégezni, majd az eredményeket csv fájlba írni.

Ha a felhasználó szeretné látni az eredményt akkor elő kell készíteni a fenti funkciókhoz szükséges változókat is. Ezért az Init függvény megkapja a felhasználó válaszát egy chk nevű booleanban.

```
#main.py
...
print('Validate results? y/n')
chk = chr(msvcrt.getch()[0]) == 'y'

Init(chk)

print("Count_of_images: " + str(pic_count))

print('Writing: ' + path_out) 
writer.writerow(["Count_of_images:," + str(pic_count)])
writer.writerow(header)
...
```

### 1.1 Fájlok beolvasása

Az Init függvény chk-tól függetlenül előkészíti az ellenőrizendő képeket. A képek mappáját megadhatjuk a Path_in változóban. A listába ebben a mappában lévő .png kiterjesztésű képek kerülnek bele. Az algoritmus ezeken az elérési utakon iterál végig.

Az eredmény azonos mappában a path_out változóval meghítározott fájba íródik.

```
#main.py
...
def Init(chk):

    global path_in
    path_in = "***/Pictures/"

    global path_out
    path_out =  path_in + "Result.csv"

    global filelist
    filelist = [f for f in os.listdir(path_in) if f.endswith(".png")]
    ...
```

### 1.2 Eredményfájl előkészítése

Az eredményfájl előkészítésénél már számít a chk értéke, ugyanis manuális validálás esetén az eredmény egyel több oszlopot tartalmaz, így a headert ennek megfelelően módosítani kell. Az eredményeket 'writer' objektumon keresztül írjuk az eredményfájlba.

A válasz és a statisztikák készítése érdekében 'chk' tól függően létrehozunk két dictinary-t is.

```
#main.py
...
def Init(chk):
    ...
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
```
### 2. Fő ciklus

A képek listájának előkészítése után azokon végigiterálunk, és a Process_img függvény segítségével feldolgozzuk azokat. Az eredények kiírható állapotra hozásáért a PrepResults függvény felel.

chk-tól függően a ciklusban megjelnítjük az eredményt és konzolunk bekérjük az esetlegesen ejtett hiba minőségét. (clustering/detection error)

Az eredményeket writeren keresztül kiírjuk.
A ciklus végén, ha készült statisztika, azt is az eredmény fájlba írjuk.

```
#main.py
...
if chk: 
    print('Press y/d/c/b to validate result.')
    
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
```

### 3. Kép előkészítés

A képeket egyesével dolgozzuk fel. első lépésként az elérési út segítségével megnyitjuk, majd szürkeárnyalatos képpé, végül adaptív gauss küszöböléssel fekete-fehér képpé alakítjuk.

Mivel a kockákon a pöttyök jól elkülönülnek a kocka színétől, ezzel a módszerrel a pöttyök éle egyértelműen kiemelhető.

![image](https://user-images.githubusercontent.com/77465523/211152238-4e750047-8199-4fbd-a63c-a7c28f8da105.png)

Az előkészített képen előbb a pöttyöket keressük meg, majd a pöttyöket csoportosítva a kockákat azonosítjuk.

```
def Process_img(pic):
    img = OpenImage(pic)
    BW_img = PreProcess(img)

    dots = GetDots(BW_img)
    dice = GetDice(dots)

    return dots, dice
```
```
#image.py
...
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
```

### 4. Pöttyök felismerése

A pontokat OpenCV SimpleBlobDetectorral keresem. A függvény paraméterei között megadható a keresett pötty minimális mérete, És annak formájára is megkötéseket tehetünk. Ezáltal ideális a kockákon lévő többnyire kör alakú pöttyök felismerésére. 
Az eredményeket látszik, hogy helyes paraméterezéssel a pöttyök 100% pontossággal kerültek felismerésre minden képen.
A pöttyöket a 'dots' array-ben tárolom amelynek egy eleme a pöttyök közepének koordinátáit, a pötty méretét, és még egyéb tulajdonságait tartalmazza.

```
#image.py
...
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
...
def GetDots(BW_img):
    dots = detector.detect(BW_img)
    return dots
```

### 5. Kockák csoportosítása

A pöttyök csoportosítását DBscan módszerrel végeztem, ugyanis ennek a clusterezésnek nem kell megadni a clusterek számát előre. Mivel a kockák száma a képen ismeretlen, ezért a clusterek számát sem tudhatjuk előre. 

DBscan a pontok távolsága alapján csoportosítja azokat. A paraméterek között eps értéke az egy csoportba tartozó pontok közötti maximális távolságot határozza meg.
Mivel a képek eltérő nagyításúak, ez a távolsák a pöttyök méretétől függ. 

Eps-t tehát dinamikusan, a képen felismert pöttyök közül a legnagyobb méretének függvényében határozom meg. Tapasztalat szerint a 6-os oldalonkét szomszédos pötty távolsága a pötty 1.4-szerese. Ezt az értéket a 'dist' változóban tárolom.

A csoportosításhoz ezután csak a pöttyök helyzete szükséges. Ezt a dots_next array tartalmazza. A dots_6 és dots_rest array-ek a lépcsős clusterezéshez szükségesek.

A clusterezés eredménye, vagyis a kockák a dice array-be íródnak. Ez az array kockánként annak középpontját, és a rajta lévő pöttyök számát tartalmazza.

```
#image.py
...
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
    ...
```
#### 5.1 Egyszerű csoportosítás

Az egyszerű csoportosításnál a pöttyök közötti legnagyobb távolság alapján csoportosítunk , azaz a 2 es oldalon lévő két átellenes pötty közötti távolság az eps paraméter értéke. 

A DBscan a cluster sorszámát jellemző label értéket rendel a pontokhoz. Ez alapján a ciklusban az egyes clusterekbe tartozó pöttyök a 'die' változóba menthetőek.

Ez a az egy kockán lévő pontokat biztosan egy csoportba sorolja, azonban egymáshoz közel lévő kockák esetén két kockát is egybe vehet.

![image](https://user-images.githubusercontent.com/77465523/211154126-52ca783d-97cb-48da-a362-34112a34fa8b.png)

Ez elég sok clusterezési hibához vezethet. Ennek elkerülésére a lépcsős clusterezési módszert mutatom be a következő fejezetben.

```
#image.py
...
def Simple_cluster(dots, dice, Factor):
    if len(dots) > 0:

        clustering = cluster.DBSCAN(eps=Factor, min_samples=1).fit(dots)

        num_dice = max(clustering.labels_) + 1
        for i in range(num_dice):
            die = dots[clustering.labels_ == i]
            centroid = np.mean(die, axis=0)
            dice.append([len(die), *centroid])
    return dice
```

#### 5.2 Lépcsős csoportosítás

A lépcsős módszer szintén DBscan módszeren alapul. Az egyetlen változás, hogy itt összesen 5 kétféle (separeting és simple) clusterezési ciklus fut le. 

A szeparáló clusterezés annyiban más, hogy kritériumként megadható, hogy hány pötty legyen egy clusterben. Ezáltal felismerhető például a csak 6-os oldal és elkülöníthető a pöttyökből. A dots_rest a maradék pontokat tartalmazza, amin aztán újabb clusterezés végezhető.

```
#image.py
...
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
```
Az 5 ciklus első lépése a 6-os oldalokon lévő 3-3 pöttyök csoportosítása. Ezek a pöttyök a többinél közelebb állnak egymáshoz, így a maradék pötty (ami nem 6-os oldalon van) a dots_rest ben marad. 

A 6-os oldal azonban 2 clusterből áll még, így ezeken a pöttyökön egy újabb simple clusterezést végzek.

Ezzel a két clusterezéssel tehát kizárólag a 6-os oldalú kockákat szűrtem ki a többi közül.

Ezután a fenti Separating_cluster függvénnyel elkülönítem a 3-as 5-ös kockákat (második legkisebb távolság a pöttyök között, madj a 4-es kockákat.
A kettesek csoportosítása a maradék pontokból az előző fejezetben leírt Simple_cluster -rel történik.

![image](https://user-images.githubusercontent.com/77465523/211154690-b5be2ab4-8eeb-41a7-a9a2-2248631afeb1.png) ![image](https://user-images.githubusercontent.com/77465523/211154843-4f3ece1c-3641-46ee-8861-4fb8a443ef21.png)


Ezzel a clusterezési hibák nagyobbik része kiszűrhető, de közel lévő 4 es vagy 2 es kockákat ez a módszer sem tud elkülöníteni.

![image](https://user-images.githubusercontent.com/77465523/211154790-0ed46b08-5b68-4e67-a7d9-4abbd780c2e0.png) ![image](https://user-images.githubusercontent.com/77465523/211154810-12ac96ff-e4ad-436c-a61d-61ea2028ac64.png)

```
#image.py
...
def GetDice(dots):
    ...
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
```

### 6. Eredmény grafikus megjelenítése

A grafikus megjelenítés a manuális ellenőrzés miatt lényeges. A pöttyöket piros körvanallal jeölölöm, a kockák középpontjára, pedig az oldalhoz rendelt pöttyök számát jelenítem meg. A fenti képeken ez látható is.

```
#image.py
...
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
```

### 7. Eredmény fájlba írása

Az eredményeket egy Results.csv fájla írom az alábbi formátumban:

Az első sor a képek számát tartalmazza, ezt követi egy header, majd az egyes képek eredményei. Pl.:

>Count_of_images:;109;;;;;;;;;;
>Picture;Response;Number_of_dice;Results;;;;;;;;
>C://Users/acer/Pictures/Pictures/Screenshot_20221113-162407.png;correct;4D;3;5;4;1;;;;;

A második oszlop 'Response' a chk (manuális ellenőrzés) től függően kerül beillesztésre.

Az utolsó sorok pedig a statisztikákat tartalmazzák (ha készült) pl.:

>correct:;0,76146789;;;;;;;;;;
>dot:;0;;;;;;;;;;
>clustering:;0,23853211;;;;;;;;;;
>both:;0;;;;;;;;;;
>unknown:;0;;;;;;;;;;

#### 7.1 Futás közbeni ellenőrzés

Ha a felhasználó ellenőrizni szeretné az eredményeket, akkor a program megjelínti azokat az Overlay függvénnyel majd vár a felhasználó válaszára a hiba minőségével kapcsolatban. 

>Correct?, y = correct, d = dot error, c = clustering error, b = both

A válasz az eredmény sorban, és a stat_dic ben tárolódik.

```
#main.py
...
def CheckResult(res):
    print(res)
    print('Correct?, y = correct, d = dot error, c = clustering error, b = both')
    print()

    resp = response_dic.get(chr(msvcrt.getch()[0]),"unknown")
    stats_dic[resp] += 1/pic_count
    res.insert(1,resp)

    return res
```
8. Összegzés.

A SimpleBlolbDetection és a Dbscan használatával a dobókockák elég jó pontossággal ismerhetőek fel. A pöttyök Gauss küszöbölés, és SimpleBlolbDetection megfelelő paraméterezésével 100% os pontossággal meghatározhatóak.

Az egyszerő DBscan módszer a clusterezést a 109 képen 76% pontossággal végezte el. Ezzel szemben a lépcsős clusterezés ugyanezen a tesztmappán 95% pontosságot ért el.
Lásd Result_Simple és Result_Complex fájlokban.

A SimpleBlolbDetection és a Dbscan viszonylag egyszerűen használható más, hasonló feladatokra is.

### 8. Források
- https://gist.github.com/qgolsteyn/261289d999a8d6288ce8c0b8472e5354
- https://www.mathworks.com/matlabcentral/answers/248036-how-to-identify-black-dots-on-dice-via-image-processing-matlab
- https://www.davidepesce.com/2019/09/06/dice-reader-part-1/
- https://golsteyn.com/writing/dice
- https://github.com/sujanay/Dice-Dot-Counter
