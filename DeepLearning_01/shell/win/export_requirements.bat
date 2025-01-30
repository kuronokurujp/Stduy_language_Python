@echo off

setlocal

cd %~dp0
call ../../venv/scripts/activate.bat
pip freeze > ../../requirements.txt

endlocal
