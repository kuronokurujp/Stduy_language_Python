@echo off

setlocal

cd %~dp0
rd /s /q build
rd /s /q dist

call ../venv/scripts/activate.bat

pyinstaller.exe ../main.py --onefile

set "YYYY=%date:~0,4%"
set "MM=%date:~5,2%"
set "DD=%date:~8,2%"
set "HH=%time:~0,2%"
set "MI=%time:~3,2%"
set "SS=%time:~6,2%"

if "%HH:~0,1%"==" " set HH=0%HH:~1,1%

set "COPY_FOLDER_PATH=..\output\%YYYY%%MM%%DD%_%HH%%MI%%SS%"
md %COPY_FOLDER_PATH%
move .\dist\main.exe %COPY_FOLDER_PATH%

rd /s /q build
rd /s /q dist
del /q .\main.spec

call ../venv/scripts/deactivate.bat


endlocal

pause
