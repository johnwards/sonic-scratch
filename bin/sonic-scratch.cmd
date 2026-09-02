@echo off
title Sonic Scratch
setlocal
cd /d "%~dp0.."

rem The installer records where it found Sonic Pi. Fall back to the usual places.
set "SONICPI="
if exist "sonicpi-path.txt" set /p SONICPI=<sonicpi-path.txt
if defined SONICPI if not exist "%SONICPI%\app\server\native\ruby\bin\ruby.exe" set "SONICPI="
if not defined SONICPI (
  for %%D in ("%ProgramFiles%\Sonic Pi" "%ProgramFiles(x86)%\Sonic Pi" "%LOCALAPPDATA%\Programs\Sonic Pi") do (
    if not defined SONICPI if exist "%%~D\app\server\native\ruby\bin\ruby.exe" set "SONICPI=%%~D"
  )
)
if not defined SONICPI (
  echo Sonic Pi was not found. Install it from https://sonic-pi.net and try again.
  pause
  exit /b 1
)

rem Host gem settings would make Sonic Pi's Ruby look in the wrong place.
set "GEM_PATH="
set "GEM_HOME="
"%SONICPI%\app\server\native\ruby\bin\ruby.exe" bridge.rb
if errorlevel 1 (
  echo.
  echo Something went wrong.
  pause
)
