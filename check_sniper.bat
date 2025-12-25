@echo off
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I /N "pythonw.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ The Sniper is RUNNING
) else (
    echo ❌ The Sniper is NOT running
)
pause