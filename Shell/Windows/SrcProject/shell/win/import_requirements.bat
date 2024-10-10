@echo off

setlocal

cd %~dp0
call venv_enable.bat
pip install -r ../../requirements.txt

endlocal
