# REW Turntable Controller unter Linux

Die GUI ist eine Python/Tkinter-Anwendung und läuft auch unter Linux, z. B. CachyOS, Arch, Debian oder Ubuntu.

## Voraussetzungen

- Python 3
- Tkinter für Python
- REW 5.40 oder neuer mit gestarteter API

Beispiele:

```bash
# Arch / CachyOS
sudo pacman -S python tk

# Debian / Ubuntu
sudo apt install python3 python3-tk
```

## Start ohne Installation

Im entpackten Ordner:

```bash
chmod +x run_gui_linux.sh
./run_gui_linux.sh
```

## Desktop-Icon installieren

Im entpackten Ordner:

```bash
chmod +x install_desktop_launcher_linux.sh
./install_desktop_launcher_linux.sh
```

Danach erscheint der Starter im Anwendungsmenü als:

```text
FM-Audio REW Turntable
```

Alternativ kann die Datei `FM-Audio-REW-Turntable.desktop` direkt auf den Desktop kopiert werden. Je nach Desktop-Umgebung muss sie danach noch als vertrauenswürdig/ausführbar markiert werden.

## Bedienung

- REW starten.
- REW-API aktivieren: `Preferences -> API -> Start API server`.
- GUI starten.
- Turntable-IP prüfen, Standard: `192.168.178.191`.
- Messmodus wählen:
  - `Auto`: automatische Sweeps, benötigt REW Pro.
  - `Manuell`: Teller dreht, Benutzer startet jede Messung in REW selbst.
  - `Nur drehen`: nur Drehtellersteuerung.
