@echo off

setlocal

cd %~dp0
call venv_enable.bat
pip freeze > ../../requirements.txt

endlocal
