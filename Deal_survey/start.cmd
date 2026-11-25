@echo off
setlocal
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -B -X utf8 "%~dp0server.py" --open-browser %*
) else if defined VIRTUAL_ENV (
    "%VIRTUAL_ENV%\Scripts\python.exe" -B -X utf8 "%~dp0server.py" --open-browser %*
) else (
    py -3.12 -B -X utf8 "%~dp0server.py" --open-browser %*
)
set "result=%errorlevel%"
if not "%result%"=="0" pause
exit /b %result%
