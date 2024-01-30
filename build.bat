@echo off
rem Run PyInstaller to create the executable
pyinstaller -F vreactable.py

rem Copy additional files to the dist folder
copy "config.ini" "dist"
copy "README.md" "dist"
rem Copy assets folder to the dist folder
xcopy /s /y "assets" "dist"

echo.
echo PyInstaller build completed.

rem Pause to keep the command prompt window open for checking errors
pause