@echo off
setlocal

echo Compiling NSIS installer...
"c:\NSIS\makensis.exe" /V4 installer.nsi > nsis_output.txt 2>&1

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Compilation successful! Installer created: PyBench-v1.3.0.0-Setup.exe
) else (
    echo.
    echo Error during compilation. Check nsis_output.txt for details.
)

endlocal
