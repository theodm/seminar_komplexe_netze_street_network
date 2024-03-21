# seminar_komplexe_netze_street_network

Dieses Repository enthält die Ergebnisse des Seminars [Komplexe Netze](https://www.fernuni-hagen.de/mi/studium/module/mskne.shtml?sg=mscinf) an der Fernuniversität Hagen aus dem WS 2023/2024 von Heinrich Böllmann und Theodor Diesner-Mayer. Der Titel der Arbeit ist **Vergleich von
Straßennetzen
hinsichtlich der
Theorie komplexer
Netze**.

## Fragestellungen

Im Rahmen der Arbeit wurden die allgemeinen Straßennetze in den Gemeinden Deutschlands hinsichtlich ihrer Small-World-Eigenschaften sowie der Skalenfreiheit untersucht. Dabei wurde auf die primale und die duale Repräsentation der Straßennetze als Graphen abgestellt und diese verglichen. Zusätzlich wurde untersucht was die verschiedenen Zentralitätsmaße über die städtischen Straßennetze bei den verschiedenen Graphenrepräsentationen aussagen.

Weitergehend wurde die (graphentheoretische) Robustheit der Straßennetze der 100 größten deutschen Städte (ohne Berlin und Hamburg) untersucht.

## Repository
In diesem Repository befinden sich:
 - Ergebnisse (ohne Bilder)
 - Skripte zur Generierung der Ergebnisse
 - Eigene Implementation des Verfahrens HICN (Hierarchical Intersection
Continuity Negotiation) bzw. ICN (von Porta et al. [1] bzw. Massuci et al [2]) basierend auf der Bibliothek StreetContinuity [3]
 - Diverse Experimente mit der Overpass-API / OSMnx und sonstigen verwendeten Biblitoheken
 - Web-Tool zur graphentheoretischen Analyse der Straßennetze
 - Präsentation der Ergebnisse (als Basis der mündlichen Leistung) [01962_Seminararbeit_Straßennetze_final.pdf](01962_Seminararbeit_Stra%C3%9Fennetze_final.pdf)
 - Schrichtliche Ausarbeitung der Ergebnisse [01962_Seminararbeit_Straßennetze_final_doc.pdf](01962_Seminararbeit_Stra%C3%9Fennetze_final_doc.pdf)


[1] S. Porta, P. Crucitti, und V. Latora, „The Network Analysis of Urban Streets: A Primal Approach“,
Environ Plann B Plann Des, Bd. 33, Nr. 5, S. 705–725, Okt. 2006, doi: 10.1068/b32045.

[2] A. P. Masucci, K. Stanilov, und M. Batty, „Exploring the evolution of London’s street network in
the information space: A dual approach“, Phys. Rev. E, Bd. 89, Nr. 1, S. 012805, Jan. 2014, doi:
10.1103/PhysRevE.89.012805.
 
[3] https://github.com/gabrielspadon/StreetContinuity

## Web-Tool
Im Rahmen der Erstellung der Arbeit ist eine kleine Webanwendung zur Analyse von den Straßennetzen in Form der primalen und dualen Repräsentation entstanden. Dieses war für das Debugging des HICN-Algorithmus und händische Analysen sehr hilfreich.

### Benutzung
Die Web-Anwendung wurde in Python und JavaScript geschrieben und befindet sich unter dem Pfad **/src/server/**.

Falls es beim Abrufen der Kartendaten zu Problemen kommt, muss ein [Stadia-Maps](https://stadiamaps.com) API-Key in der Datei **/src/srver/client/stadia-api-key.js** als Default-Export hinterlegt werden. 

Der Server kann dann mittels der Datei **/src/server/server.py** gestartet werden. Er läuft standardmäßig auf dem Post 8080.

### graph_tool und PyIntergraph
Das Web-Tool erfordert die Bibliotheken graph_tool und pyintergraph. Graph_tool ist leider nur für Linux erhältlich. PyIntergraph wurde mittels Monkey-Patching modifiziert, da die Konvertierung fehlgeschlagen ist. Die korrigierte Version der Graph.py ist im Ordner ***/pyintergraph/Graph.py** zu finden.

### Funktionalitäten
 
 - Anzeige von Koordinaten und Bounding-Koordinaten
 - Laden von Graphen mittels Geocode
 - Anzeige von Basis-Grapheninformationen über den dualen Graphen und primalen Graphen
 - Anzeige des primalen Graphen und dualen Graphen von Straßennetzen
 - Anzeige von Informationen von Knoten und Kanten
 - Anzeige der Relative-Betweenness des primalen oder dualen Graphen
 - Anzeige unterschiedlicher Graphentypen (MultiDiGraph, MultiGraph, DiGraph, Graph)

### Bilder

#### Anzeige des primalen Graphen

![img1.png](docs/img1.png)

#### Anzeige des primalen Graphen (mit Relative Betweenness)
![img2.png](docs/img2.png)

#### Anzeige des dualen Graphen (Knoten koloriert)
![img3.png](docs/img3.png)

#### Anzeige des dualen Graphen (koloriert nach Knotengrad)
![img4.png](docs/img4.png)

#### Anzeige von Detailinformationen zu einer Kante
![img5.png](docs/img5.png)

## Finale Präsentation (mündliche Leistung)

![01962_Präsentation_Straßennetze_final-01.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-01.png)
![01962_Präsentation_Straßennetze_final-02.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-02.png)
![01962_Präsentation_Straßennetze_final-03.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-03.png)
![01962_Präsentation_Straßennetze_final-04.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-04.png)
![01962_Präsentation_Straßennetze_final-05.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-05.png)
![01962_Präsentation_Straßennetze_final-06.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-06.png)
![01962_Präsentation_Straßennetze_final-07.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-07.png)
![01962_Präsentation_Straßennetze_final-08.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-08.png)
![01962_Präsentation_Straßennetze_final-09.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-09.png)
![01962_Präsentation_Straßennetze_final-10.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-10.png)
![01962_Präsentation_Straßennetze_final-11.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-11.png)
![01962_Präsentation_Straßennetze_final-12.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-12.png)
![01962_Präsentation_Straßennetze_final-13.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-13.png)
![01962_Präsentation_Straßennetze_final-14.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-14.png)
![01962_Präsentation_Straßennetze_final-15.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-15.png)
![01962_Präsentation_Straßennetze_final-16.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-16.png)
![01962_Präsentation_Straßennetze_final-17.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-17.png)
![01962_Präsentation_Straßennetze_final-18.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-18.png)
![01962_Präsentation_Straßennetze_final-19.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-19.png)
![01962_Präsentation_Straßennetze_final-20.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-20.png)
![01962_Präsentation_Straßennetze_final-21.png](docs%2F01962_Pr%C3%A4sentation_Stra%C3%9Fennetze_final-21.png)