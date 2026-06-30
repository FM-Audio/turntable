# REW Turntable Controller unter Windows

Die GUI ist mit Python/Tkinter gebaut und läuft unter Windows, Linux und macOS.

## Voraussetzungen

1. REW 5.40 oder neuer starten.
2. In REW den API-Server aktivieren:
   `Preferences -> Schnittstelle (API) -> Start server`
3. Python 3 von <https://www.python.org/downloads/windows/> installieren.
   Wichtig: Tkinter ist beim offiziellen Python-Installer normalerweise enthalten.

## Start

Im Ordner `software\rew_turntable` doppelklicken:

```text
run_gui_windows.bat
```

Oder in PowerShell:

```powershell
cd software\rew_turntable
py -3 rew_turntable_gui.py
```

## Bedienung

- `Start °`, `Ende °`, `Schritt °`: Winkelreihe, z. B. `0` bis `135` in `10` Grad Schritten.
- `Startfrequenz Hz`, `Endfrequenz Hz`: REW-Sweepbereich, z. B. Hochtöner `2000` bis `20000` Hz.
- `Modus Auto`: Ablauf läuft automatisch: Teller dreht -> REW-Sweep startet -> Programm wartet bis Messung da ist -> nächster Winkel. Dafür muss eine REW-Pro-Upgrade-Lizenz in REW hinterlegt sein.
- `Modus Manuell`: Teller dreht -> Benutzer startet Messung in REW -> Programm wartet bis Messung da ist -> nächster Winkel.

Hinweis: Das automatische Starten von REW-Sweeps per API und das Ändern des Sweep-Frequenzbereichs per API benötigen das REW-Pro-Upgrade. Wenn REW das ablehnt, den manuellen Modus verwenden oder Pro in REW aktivieren.
