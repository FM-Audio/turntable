@echo off
setlocal
REM REW Turntable Controller - Windows launcher
REM Requirements: Python 3 with tkinter (standard python.org installer includes tkinter)
cd /d "%~dp0"
py -3 rew_turntable_gui.py
if errorlevel 1 (
  echo.
  echo Python launcher 'py' failed. Trying python.exe...
  python rew_turntable_gui.py
)
pause
