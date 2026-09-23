@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD=python"
where py >nul 2>nul && set "PYTHON_CMD=py"

where %PYTHON_CMD% >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python first.
  goto :error
)

set "WORKBOOK="
for %%F in (*.xlsx) do if not defined WORKBOOK set "WORKBOOK=%%F"
if not defined WORKBOOK (
  echo No Excel workbook was found in this folder.
  goto :error
)

%PYTHON_CMD% -c "import openpyxl; from PIL import Image" >nul 2>nul
if errorlevel 1 (
  echo Installing required components...
  %PYTHON_CMD% -m pip install -r requirements.txt
  if errorlevel 1 goto :error
)

%PYTHON_CMD% import_profiles_excel.py "%WORKBOOK%"
if errorlevel 1 goto :error

echo.
echo Site update completed. Preview dist\index.html before uploading.
pause
exit /b 0

:error
echo.
echo Site update failed. Keep this window open and check the message above.
pause
exit /b 1
