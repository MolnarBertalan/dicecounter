# Dobókocka felismerés

A program célja klasszikus 6 oldalú dobókockákról készült képen a pöttyök felismerése, és az egyes kockák elkülönítése, a kockákkal dobott értékek meghatározása.

Mivel alapvető elvárás a dobókockákkal szemben, hogy emberi szem által is könnyen olvashatóak legyenek. Ezért feltételezhetem, hogy a pöttyök és a kockatest színe jól elkülönül egymástól. Ez alapján a pöttyök éle valószínűleg könnyen felismerhető. 

A dobókockák azonosítását ezután a pöttyök csoportosításával lehet például elvégezni. Az egyes kockákon lévő pöttyök egymáshoz nagy valószínűséggel közelebb álnak, mint a többi pöttyhöz. Ezt clusterezési módszerekkel lehet megoldani.

Az algoritmust a repositroyban megtalálható 109 képen teszteltem amelyek kölünböző színű, helyzetű, darabszámú kockákról készültek, eltérő hátterek előtt és különböző nagyításban.

A képeket egy androidos dobókockaszimulátor applikáció segítségével készítettem, ahol lehet változtatni a kockák színét, darabszámát, a háttér színét, és a nagyítást is.
Az eredményt csv fájlokban rögzítettem. Result_True a 100% ban pontos (természetesen emberi) eredményt tartalmazza összehasonlítás érdekében.

A feladat során több hibát okozott, hogy a clusterezés során egymáshoz közel álló kockák egy clusterbe kerültek, mivel a 2 es oldalon a pöttyök távolsága viszonylag nagy. 

Ezt lépcsős clusterezéssel igyekeztem kiküszöbölni, ami 4 lépésben azonosítja a kockákat. Előbb a 6-os oldalakat, majd egyszerre a 3-as, 5-ös dobásokat, harmadjára a 4-est, és végül a 2-es, 1-es csoportokat. 

Ezzel az egymáshoz közel álló 6,3,5 ös oldalak egyértelműen elkülöníthetőek, a 4-es, 2-es viszont még okozott nehézséget.
