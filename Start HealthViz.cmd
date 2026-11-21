@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sys; sys.exit(sys.version_info < (3,8))" >nul 2>&1
if not errorlevel 1 (
    py -3 app.py
    goto done
)
for /f "delims=" %%P in ('where python.exe 2^>nul ^| findstr /i /v "\\WindowsApps\\"') do (
    "%%P" -c "import sys; sys.exit(sys.version_info < (3,8))" >nul 2>&1
    if not errorlevel 1 (
        "%%P" app.py
        goto done
    )
)
for /f "delims=" %%P in ('dir /b /ad /o-n "%ProgramFiles%\WindowsApps\OpenAI.CodexPrimaryRuntime.*" 2^>nul') do (
    "%ProgramFiles%\WindowsApps\%%P\dependencies\python\python.exe" -c "import sys; sys.exit(sys.version_info < (3,8))" >nul 2>&1
    if not errorlevel 1 (
        "%ProgramFiles%\WindowsApps\%%P\dependencies\python\python.exe" app.py
        goto done
    )
)
echo Python 3.8 or newer is required: https://www.python.org/downloads/windows/
goto end
:done
if not errorlevel 1 exit /b
echo HealthViz could not start. See the error above.
:end
pause
