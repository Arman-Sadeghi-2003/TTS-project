@echo off
REM Launcher for tts.py. Keeps every cache and temp file inside L:\TTS-project.
set "PROJECT=L:\TTS-project"

set "PIP_CACHE_DIR=%PROJECT%\cache\pip"
set "TEMP=%PROJECT%\cache\temp"
set "TMP=%PROJECT%\cache\temp"
set "PYTHONPYCACHEPREFIX=%PROJECT%\cache\pycache"
set "PYTHONUTF8=1"

if not exist "%PROJECT%\venv\Scripts\python.exe" (
    echo Virtual environment not found at %PROJECT%\venv
    exit /b 1
)

"%PROJECT%\venv\Scripts\python.exe" "%PROJECT%\tts.py" %*
