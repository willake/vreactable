@ECHO OFF

rmdir /s /q "dist"
mkdir "dist"

ECHO Copy additional files to the dist folder
copy "config.ini" "dist"
copy "README.md" "dist"
ECHO Copy assets folder to the dist folder
mkdir "dist/assets"
xcopy /s /y "assets" "dist/assets"

ECHO.
ECHO PyInstaller build completed.

ECHO Run PyInstaller to create the executable
pyinstaller -F vreactable.py

rem Pause to keep the command prompt window open for checking errors
PAUSE