# REW-Integration für den FM-Audio Turntable

Der bestehende Drehteller wurde ursprünglich für ARTA gebaut. REW 5.40+ besitzt inzwischen eine HTTP-API, dadurch kann der Drehteller auch mit REW automatisiert werden.

## Kurzfazit

Ja, die Anbindung ist möglich.

Für den vollautomatischen Betrieb muss in REW eine **Pro-Upgrade-Lizenz** hinterlegt sein. Das ist wichtig für Benutzer des GitHub-Repos:

- automatische Sweeps per API: `POST /measure/command {"command": "SPL"}`
- Sweep-Frequenzbereich per API setzen: `PUT /measure/sweep/configuration`

Ohne Pro bleibt der manuelle Modus nutzbar: Das Programm dreht den Teller und wartet, bis der Benutzer in REW eine Messung gestartet/gespeichert hat.

Es gibt drei Betriebsarten:

| Modus | Voraussetzung | Ablauf |
|---|---|---|
| `auto` | REW 5.40+ API + REW Pro Upgrade | Programm dreht den Teller, startet den REW-Sweep per API, wartet bis die Messung fertig in REW erscheint, dreht weiter |
| `manual` | REW 5.40+ API, keine Pro-Lizenz nötig | Programm dreht den Teller, Bediener startet Messung in REW, Programm erkennt neue Messung |
| `turntable-only` | nur Netzwerk zum Arduino | Programm dreht nur den Teller |

Wichtig: Laut REW-Dokumentation sind GET-Zugriffe frei nutzbar. Schreibende API-Aktionen wie Sweep-Konfiguration und automatisierte Sweep-Messungen benötigen das REW-Pro-Upgrade.

## Architektur

```text
REW 5.40+ API  <---- HTTP localhost:4735 ---->  rew_turntable_runner.py
                                                        |
                                                        | UDP Port 10049
                                                        v
Arduino Turntable  <---- TB6600 ---->  NEMA23 / Drehteller
```

Der Arduino-Code muss dafür zunächst nicht geändert werden. Er versteht bereits UDP-Kommandos mit Winkelwerten.

## Vorhandenes Arduino-Protokoll

Im Arduino-Sketch:

```cpp
unsigned int localPort = 10049;
float Stepsprograd = 65.75;
```

Der Arduino erwartet per UDP einen Winkel als ASCII-Text, z. B.:

```text
0
15
30
-15
```

Danach fährt er auf diese Position und sendet eine kurze Textantwort zurück.

## REW API starten

### Windows

```powershell
"C:\Program Files\REW\roomeqwizard.exe" -api
```

Oder in den REW-Einstellungen:

```text
Preferences -> API -> Start API server
```

Standardadresse:

```text
http://127.0.0.1:4735
```

Die Swagger-/API-Doku ist dann im Browser erreichbar:

```text
http://localhost:4735
```

### Prüfen

Auf dem REW-PC:

```powershell
curl http://127.0.0.1:4735/application/commands
```

Wenn JSON zurückkommt, läuft die API.

## REW wie ARTA nutzen

ARTA hat eine eingebaute Gruppenmessung:

```text
Record -> Spatial impulse response group record
```

Dort stellt man z. B. `0°` bis `90°` in `15°`-Schritten ein. ARTA ruft dann für jeden Winkel `turntable.exe` auf.

REW hat aktuell keine identische eingebaute Turntable-Dialogbox. Die entsprechende Lösung ist daher ein **kleiner externer Ablaufstarter**:

```text
rew_turntable_runner.py
```

Der Ablaufstarter übernimmt das, was bei ARTA die Gruppenmessung macht:

1. Winkelreihe erzeugen, z. B. `0, 15, 30, 45, 60, 75, 90`.
2. Drehteller per UDP auf den Zielwinkel fahren.
3. Einschwingzeit abwarten.
4. REW-Messung starten oder auf manuell gestartete REW-Messung warten.
5. Messung mit Winkelname/Notiz versehen.
6. Zum nächsten Winkel gehen.

Damit sieht der REW-Ablauf praktisch so aus:

```bash
python software/rew_turntable/rew_turntable_runner.py \
  --turntable-ip 192.168.178.191 \
  --mode manual \
  --angles 0:90:15 \
  --settle-s 3 \
  --name-template "Angle {angle} deg"
```

Für den Standardfall liegt zusätzlich ein Starter-Script im gleichen Ordner:

```bash
software/rew_turntable/run_0_90_15_manual.sh
```

Für den normalen Werkstattbetrieb gibt es außerdem ein kleines Desktop-Fenster:

```bash
python software/rew_turntable/rew_turntable_gui.py
```

Dort können Startwinkel, Endwinkel, Schrittweite und der REW-Frequenzbereich frei eingegeben werden, z. B.:

```text
Start: 0°
Ende:  135°
Schritt: 10°
Startfrequenz: 2000 Hz
Endfrequenz: 20000 Hz
```

Der Frequenzbereich wird über die REW-API gesetzt:

```http
PUT /measure/sweep/configuration
{"startFrequency": 2000, "endFrequency": 20000, "length": "512k"}
```

Das ist z. B. für Hochtöner sinnvoll, damit kein unnötiger Tieftonanteil im Sweep liegt.

Das erzeugt die Reihe:

```text
0°, 10°, 20°, 30°, 40°, 50°, 60°, 70°, 80°, 90°, 100°, 110°, 120°, 130°, 135°
```

Wenn der Endwinkel nicht genau auf dem Raster liegt, wird er als letzter Winkel zusätzlich angefahren. So funktioniert `0°` bis `135°` mit `10°` Schritten wie erwartet.

Für den Bediener ist das die REW-Entsprechung zu ARTA `Start` in der Gruppenmessung.

## Script verwenden

Das Script liegt hier:
```text
software/rew_turntable/rew_turntable_runner.py
```

### Nur Drehteller testen

```bash
python software/rew_turntable/rew_turntable_runner.py \
  --turntable-ip 192.168.178.191 \
  --mode turntable-only \
  --angles 0
```

### Manuell mit REW messen

Dieser Modus braucht keine REW-Pro-Lizenz für automatische Sweeps.

```bash
python software/rew_turntable/rew_turntable_runner.py \
  --turntable-ip 192.168.178.191 \
  --mode manual \
  --angles 0:180:15 \
  --settle-s 3
```

Ablauf:

1. Script fährt Winkel 0° an.
2. Script wartet 3 Sekunden.
3. Bediener startet in REW die Messung.
4. Script erkennt, dass eine neue Messung in REW entstanden ist.
5. Script fährt zum nächsten Winkel.
6. Wiederholen bis Endwinkel erreicht ist.

### Vollautomatisch mit REW Pro

```bash
python software/rew_turntable/rew_turntable_runner.py \
  --turntable-ip 192.168.178.191 \
  --mode auto \
  --angles 0:180:15 \
  --settle-s 3 \
  --start-frequency 2000 \
  --end-frequency 20000 \
  --sweep-length 512k
```

Dieser Modus läuft so ab:

1. REW-Sweepbereich konfigurieren, z. B. 2000–20000 Hz.
2. Drehteller auf den Zielwinkel fahren.
3. Einschwingzeit abwarten.
4. REW-API-Befehl senden:

```http
POST /measure/command
{"command": "SPL"}
```

5. Warten, bis in REW eine neue Messung unter `/measurements` erscheint.
6. Erst dann zum nächsten Winkel fahren.

Wenn REW meldet, dass die Lizenz nicht ausreicht, `--mode manual` verwenden oder REW Pro aktivieren.

## Wenn REW auf einem anderen Rechner läuft

Die REW-API ist standardmäßig nur lokal erreichbar. Am einfachsten ist daher:

- Python-Script direkt auf dem REW-PC ausführen.
- Der REW-PC muss den Arduino per Netzwerk erreichen können.

Alternativ kann REW mit Host-Bindung gestartet werden:

```powershell
"C:\Program Files\REW\roomeqwizard.exe" -api -host "0.0.0.0"
```

Dann Firewall und Netzwerkfreigabe beachten.

## Aktuell geprüfter Turntable

Im lokalen Netzwerk wurde der Arduino anhand der im Sketch definierten MAC-Adresse gefunden:

```text
MAC: b8:96:74:01:02:03
IP:  192.168.178.191
Port: 10049/UDP
```

Ein sicherer Test mit Winkel `0` lieferte eine UDP-Antwort vom Arduino.

## Nächste technische Verbesserungen

- Arduino-Antwort verlängern: Der aktuelle Antwortpuffer ist sehr kurz und schneidet den Text ab.
- Optional Statuskommando ergänzen, z. B. `status`, ohne Bewegung.
- Optional `home`/`reference`-Kommando ergänzen.
- Optional Zielwinkel erst bestätigen, wenn die Position wirklich erreicht wurde.
- Python-Script später als Windows-EXE paketieren.
