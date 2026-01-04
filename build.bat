@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Building executable...
pyinstaller --name=FileClassify --windowed --onefile src/main.py

echo.
echo Build complete! Executable is in dist/FileClassify.exe
pause
