# Downloads

Dieses Repository enthält Hardware-Dateien, Firmware und Software-Starter für den FM-Audio Drehteller.

## Schnellübersicht

| Paket / Datei | Zweck | Wo herunterladen? |
|---|---|---|
| Komplettes Projekt | Firmware, CAD, Bilder, Doku, Software | GitHub: `Code -> Download ZIP` |
| Windows GUI | Fertige `FM-Audio-REW-Turntable.exe` für REW | GitHub `Actions -> Build GUI Downloads -> neuester erfolgreicher Lauf -> Artifacts -> FM-Audio-REW-Turntable-Windows` |
| Linux GUI + Desktop-Icon | Python/Tkinter-GUI, Shell-Starter, `.desktop`-Launcher | GitHub `Actions -> Build GUI Downloads -> neuester erfolgreicher Lauf -> Artifacts -> FM-Audio-REW-Turntable-Linux` |
| ARTA-Treiber | Klassische ARTA-Datei `turntable.exe` | Im Repo: `ARTA Turntable File/turntable.exe` |
| STEP/CAD | STEP-Datei für den Drehteller | Im Repo: `Drehteller.zip` |
| DXF-Dateien | Fräs-/Laser-Dateien | Im Repo: `DXF/` |
| STL-Dateien | 3D-Druckteile | Im Repo: `STL/` |

## Windows

1. Auf GitHub den Reiter `Actions` öffnen.
2. Workflow `Build GUI Downloads` auswählen.
3. Den neuesten grünen Lauf öffnen.
4. Unter `Artifacts` herunterladen:

```text
FM-Audio-REW-Turntable-Windows
```

5. ZIP entpacken und starten:

```text
FM-Audio-REW-Turntable.exe
```

## Linux / CachyOS / Arch

1. Auf GitHub den Reiter `Actions` öffnen.
2. Workflow `Build GUI Downloads` auswählen.
3. Den neuesten grünen Lauf öffnen.
4. Unter `Artifacts` herunterladen:

```text
FM-Audio-REW-Turntable-Linux
```

5. ZIP entpacken.
6. Voraussetzungen installieren, z. B. auf CachyOS/Arch:

```bash
sudo pacman -S python tk
```

7. Direkt starten:

```bash
chmod +x run_gui_linux.sh
./run_gui_linux.sh
```

8. Optional Desktop-Icon installieren:

```bash
chmod +x install_desktop_launcher_linux.sh
./install_desktop_launcher_linux.sh
```

Danach gibt es einen Anwendungsstarter:

```text
FM-Audio REW Turntable
```

## Hinweis zu GitHub Actions Artifacts

GitHub-Actions-Artefakte sind für einfache Downloads praktisch, können aber nach einiger Zeit ablaufen. Für dauerhaft versionierte Downloads sollte zusätzlich eine GitHub Release mit den ZIP-Dateien erstellt werden.
