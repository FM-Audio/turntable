# Troubleshooting

## Display zeigt keine IP-Adresse

Mögliche Ursachen:

- Netzwerkkabel nicht angeschlossen
- DHCP im Router nicht aktiv
- Ethernet-Shield nicht korrekt gesteckt
- falsches Board ausgewählt

Prüfen:

1. Serial Monitor der Arduino IDE öffnen.
2. Arduino neu starten.
3. Meldungen zu DHCP prüfen.

Im Code gibt es einen Fallback:

```cpp
IPAddress ip(165, 166, 167, 100);
```

Diese Adresse passt in den meisten Heimnetzwerken nicht und sollte bei Bedarf angepasst werden.

## Referenzfahrt bleibt hängen

Mögliche Ursachen:

- Sensor falsch angeschlossen
- Sensor invertiert
- Abstand Sensor/Trigger falsch
- Pin D3 nicht korrekt verbunden

Im Code:

```cpp
#define Referenzpunkt 3
pinMode(Referenzpunkt, INPUT_PULLUP);
```

Prüfen, ob der Sensor im Serial Monitor bzw. mit einem einfachen Testsketch HIGH/LOW korrekt wechselt.

## Motor dreht nicht

Mögliche Ursachen:

- 24-V-Netzteil aus
- TB6600 falsch verdrahtet
- Motorwicklungen falsch zugeordnet
- Enable-Signal falsch
- Treiberstrom zu niedrig

Prüfen:

- TB6600-Spannung
- Motorwicklungen mit Multimeter
- STEP an Arduino D2
- DIR an Arduino D5
- GND-Bezug

## Motor läuft falsch herum

Lösung:

- DIR-Logik ändern,
- Motorwicklung tauschen,
- Richtung im Code anpassen.

## Winkel stimmt nicht

Ursache ist meist ein falscher Kalibrierwert:

```cpp
float Stepsprograd = 65.75;
```

Siehe [`calibration.md`](calibration.md).

## Motor verliert Schritte

Mögliche Ursachen:

- Beschleunigung zu hoch
- Geschwindigkeit zu hoch
- Motorstrom falsch eingestellt
- Mechanik schwergängig
- Last zu groß

Im Code prüfen:

```cpp
stepper.setMaxSpeed(500);
stepper.setAcceleration(1000);
```

Zum Testen beide Werte reduzieren.

## ARTA startet keine Bewegung

Prüfen:

- Ist `turntable.exe` in ARTA eingetragen?
- Blockiert die Windows-Firewall?
- Ist Arduino im Netzwerk erreichbar?
- Wird die IP-Adresse auf dem Display angezeigt?
- Sind PC und Arduino im gleichen Netzwerk?

## Motor wird heiß

Mögliche Ursachen:

- Haltestrom am TB6600 zu hoch
- Enable/Disable nicht korrekt
- Motor bleibt dauerhaft bestromt

Im Sketch wird nach Bewegungen deaktiviert:

```cpp
stepper.disableOutputs();
```

Trotzdem Treiberstrom und Enable-Logik prüfen.
