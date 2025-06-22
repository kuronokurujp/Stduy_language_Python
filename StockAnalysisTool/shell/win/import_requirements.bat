@echo off

setlocal

cd %~dp0
call ../../venv/scripts/activate.bat
pip install -r ../../requirements.txt

endlocal
