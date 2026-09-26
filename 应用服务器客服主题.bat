@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD=python"
where py >nul 2>nul && set "PYTHON_CMD=py"

where %PYTHON_CMD% >nul 2>nul
if errorlevel 1 (
  echo Python was not found.
  goto :error
)

%PYTHON_CMD% -u apply_server_chat_only.py
if errorlevel 1 goto :error

echo.
echo Update completed. Preview dist\index.html before uploading.
pause
exit /b 0

:error
echo.
echo Update failed. Excel and content data were not replaced.
pause
exit /b 1
