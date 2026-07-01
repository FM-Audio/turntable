# Downloads

Dieses Repository enthält Hardware-Dateien, Firmware und Software-Starter für den FM-Audio Drehteller.

## Schnellübersicht

| Paket / Datei | Zweck | Wo herunterladen? |
|---|---|---|
| Komplettes Projekt | Firmware, CAD, Bilder, Doku, Software | GitHub: `Code -> Download ZIP` |
| Windows GUI | Fertige `FM-Audio-REW-Turntable.exe` für REW | GitHub `Releases` -> `FM-Audio-REW-Turntable-Windows.zip` |
| Linux GUI + Desktop-Icon | Python/Tkinter-GUI, Shell-Starter, `.desktop`-Launcher | GitHub `Releases` -> `FM-Audio-REW-Turntable-Linux.zip` |
| ARTA-Treiber | Klassische ARTA-Datei `turntable.exe` | Im Repo: `ARTA Turntable File/turntable.exe` |
| STEP/CAD | STEP-Datei für den Drehteller | Im Repo: `Drehteller.zip` |
| DXF-Dateien | Fräs-/Laser-Dateien | Im Repo: `DXF/` |
| STL-Dateien | 3D-Druckteile | Im Repo: `STL/` |

## Windows

1. Auf GitHub den Bereich `Releases` öffnen:

```text
https://github.com/FM-Audio/turntable/releases
```

2. Das Windows-Paket herunterladen:

```text
FM-Audio-REW-Turntable-Windows.zip
```

3. ZIP entpacken und starten:

```text
FM-Audio-REW-Turntable.exe
```

## Linux / CachyOS / Arch

1. Auf GitHub den Bereich `Releases` öffnen:

```text
https://github.com/FM-Audio/turntable/releases
```

2. Das Linux-Paket herunterladen:

```text
FM-Audio-REW-Turntable-Linux.zip
```

3. ZIP entpacken.
4. Voraussetzungen installieren, z. B. auf CachyOS/Arch:

```bash
sudo pacman -S python tk
```

5. Direkt starten:

```bash
chmod +x run_gui_linux.sh
./run_gui_linux.sh
```

6. Optional Desktop-Icon installieren:

```bash
chmod +x install_desktop_launcher_linux.sh
./install_desktop_launcher_linux.sh
```

Danach gibt es einen Anwendungsstarter:

```text
FM-Audio REW Turntable
```

## Actions-Artefakte

Zusätzlich erzeugt der Workflow `Build GUI Downloads` weiterhin GitHub-Actions-Artefakte. Für normale Nutzer sind aber die Dateien im Bereich `Releases` der empfohlene Download-Weg.
