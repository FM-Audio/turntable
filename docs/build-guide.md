# Aufbau und Projektüberblick

Dieser Drehteller wurde entwickelt, um Lautsprecher bei ARTA-Messungen automatisch auf definierte Winkel zu drehen.

## Problem

Für Directivity- und Polar-Messungen müssen Lautsprecher unter vielen Winkeln gemessen werden. Bei einer manuellen Lösung muss man nach jeder Messung:

1. Messung stoppen oder neu starten,
2. Dateinamen kontrollieren,
3. Lautsprecher manuell weiterdrehen,
4. nächsten Winkel messen.

Das ist langsam und bei wiederholten Entwicklungszyklen unpraktisch.

## Ziel der Lösung

Die Lösung soll:

- mit gut verfügbaren Standardteilen funktionieren,
- per Netzwerk steuerbar sein,
- unabhängig von langen USB-Kabeln arbeiten,
- den aktuellen Status sichtbar anzeigen,
- direkt mit ARTA nutzbar sein.

## Aufbau

Die Mechanik besteht aus einem Drehkranz, einem Schrittmotor mit Ritzel und einer Trägerplatte. Der Schrittmotor wird über einen TB6600-Treiber angesteuert.

Der Arduino übernimmt:

- Netzwerkverbindung über Ethernet,
- Empfang des Zielwinkels per UDP,
- Referenzfahrt über einen Sensor,
- Umrechnung von Winkel in Motorschritte,
- Ansteuerung des Schrittmotors,
- Anzeige von IP-Adresse und Position auf dem LCD.

## Dateiübersicht

| Bereich | Datei / Ordner |
|---|---|
| Firmware | `Arduino/Arta_TurntablemitStepperundDisplay20230803.ino` |
| ARTA-Treiber | `ARTA Turntable File/turntable.exe` |
| Anschlussplan | `Bilder/Anschlussplan.png` |
| Stückliste | `Bestellliste.xlsx` |
| CAD/DXF | `DXF/` |
| 3D-Druck | `STL/` |
| STEP/CAD | `Drehteller.zip` |

## Startablauf

1. Arduino startet.
2. Display wird initialisiert.
3. Arduino versucht per DHCP eine IP-Adresse zu erhalten.
4. IP-Adresse wird angezeigt.
5. UDP-Port `10049` wird geöffnet.
6. Referenzfahrt startet.
7. Drehteller ist bereit für ARTA.

## Hinweis zur Mechanik

Der Wert `Stepsprograd` im Arduino-Code muss zur realen Übersetzung passen. Wenn Zahnrad, Motor, Microstepping oder Drehkranz geändert werden, muss dieser Wert neu kalibriert werden.

Siehe: [`calibration.md`](calibration.md)
