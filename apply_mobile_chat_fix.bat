@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 goto use_python

py -3 "%~dp0apply_mobile_chat_site_fix.py"
goto finished

:use_python
python "%~dp0apply_mobile_chat_site_fix.py"

:finished
set PATCH_RESULT=%errorlevel%
echo.
echo Patch finished with exit code %PATCH_RESULT%.
pause
exit /b %PATCH_RESULT%
