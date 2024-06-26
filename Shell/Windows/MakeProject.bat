@echo off
chcp 65001

echo python開発プロジェクトを作成します
echo 途中で作成を止めたければバッチ実行を強制終了してください。

echo 入力指示に従ってください

setlocal
SET BAT_FULLPATH=%~dp0

:INPUT_DIR_FULLPATH
echo プロジェクトを作成するディレクトリ先の絶対パスを入力してください
SET DIR_FULLPATH=
SET /P DIR_FULLPATH=
IF "%DIR_FULLPATH%"=="" GOTO :INPUT_DIR_FULLPATH

echo +-------------------------------------------------------+
echo パスは[%DIR_FULLPATH%]でよろしいですか？
echo Y/N
echo +-------------------------------------------------------+
SET CONF_SELECT=
SET /P CONF_SELECT=

IF "%CONF_SELECT%"== SET CONF_SELECT=Y
IF /I NOT "%CONF_SELECT%"=="Y"  GOTO :INPUT_DIR_FULLPATH

:INPUT_DIR_NAME
echo プロジェクト名を入力してください
SET DIR_NAME=
SET /P DIR_NAME=
IF "%DIR_NAME%"=="" GOTO :INPUT_DIR_NAME

ECHO +-------------------------------------------------------+
ECHO プロジェクト名は[%DIR_NAME%]でよろしいですか？
ECHO Y/N
ECHO +-------------------------------------------------------+
SET CONF_SELECT=
SET /P CONF_SELECT=

IF "%CONF_SELECT%"== SET CONF_SELECT=Y
IF /I NOT "%CONF_SELECT%"=="Y"  GOTO :INPUT_DIR_NAME

:INPUT_USE_PYTHON_VERSION
echo pyenvでインストールしているpython一覧
call pyenv.bat versions
REM pyenv.batを呼び出すとUTF8文字コード設定がキャンセルされるので再設定
chcp 65001

echo pyenvでインストールしているPythonのVersionを入力してください

SET USE_PYTHON_VERSION=
SET /P USE_PYTHON_VERSION=
IF "%USE_PYTHON_VERSION%"=="" GOTO :INPUT_USE_PYTHON_VERSION

echo +-------------------------------------------------------+
echo Pythonバージョンは[%USE_PYTHON_VERSION%]でよろしいですか？
echo Y/N
echo +-------------------------------------------------------+
SET CONF_SELECT=
SET /P CONF_SELECT=

IF "%CONF_SELECT%"== SET CONF_SELECT=Y
IF /I NOT "%CONF_SELECT%"=="Y"  GOTO :INPUT_USE_PYTHON_VERSION

REM ディレクトリ作成
echo プロジェクトのディレクトリを作成します
cd %DIR_FULLPATH%
if %errorlevel% == 0 (
    echo カレントディレクトリ[%DIR_FULLPATH%]に成功しました
) else (
    echo カレントディレクトリ[%DIR_FULLPATH%]に失敗しました
    pause
    exit /B -1
)

md %DIR_NAME%
if %errorlevel% == 0 (
    echo ディレクトリ作成[%DIR_FULLPATH%/%DIR_NAME%]に成功しました
) else (
    echo ディレクトリ作成[%DIR_NAME%]に失敗しました
    pause
    exit /B -1
)

REM 以後はプロジェクトディレクトリをカレントディレクトリにする
set PROJECT_DIR_FULLPATH=%DIR_FULLPATH%/%DIR_NAME%
cd %PROJECT_DIR_FULLPATH%
if %errorlevel% == 0 (
    echo カレントディレクトリ[%DIR_FULLPATH%/%DIR_NAME%]に成功しました
) else (
    echo カレントディレクトリ[%DIR_FULLPATH%/%DIR_NAME%]に失敗しました
    pause
    exit /B -1
)

REM pyenvで利用するpythonを指定
call pyenv.bat local %USE_PYTHON_VERSION%
REM 呼び出すとUTF8文字コード設定がキャンセルされるので再設定
chcp 65001
if %errorlevel% == 0 (
    echo pyenv local %USE_PYTHON_VERSION% に成功しました
) else (
    echo pyenv local %USE_PYTHON_VERSION% に失敗しました
    pause
    exit /B -1
)

REM pythonの仮想環境を作る
echo pythonの仮想環境を作成します
call python -m venv venv
REM 呼び出すとUTF8文字コード設定がキャンセルされるので再設定
chcp 65001
if %errorlevel% == 0 (
    echo pyenv -m venv venv に成功しました
) else (
    echo pyenv -m venv venv に失敗しました
    pause
    exit /B -1
)

REM 仮想環境に切り替え
call venv\Scripts\activate.bat
chcp 65001

REM pipの更新
call python.exe -m pip install --upgrade pip
chcp 65001

REM 必須パッケージをpipでインストール
call pip install black
call pip install flake8
call pip install pytest
chcp 65001

REM vscode環境を作成
set VSCODE_SRC_PROJ_FULLPATH=%BAT_FULLPATH%SrcProject
echo VSCodeの[%VSCODE_SRC_PROJ_FULLPATH%]開発環境をコピーします
xcopy %VSCODE_SRC_PROJ_FULLPATH% . /D /S /R /Y /I /K
if %errorlevel% == 0 (
    echo VSCodeでの開発環境に成功しました
) else (
    echo VSCodeでの開発環境に失敗しました
    pause
    exit /B -1
)

REM 開発環境ファイルを修正
REM vscodeのjsonファイルではパス区切りは/にしないとだめ
set VSCODE_PROJECT_DIR_FULLPATH=%PROJECT_DIR_FULLPATH:\=/%

REM launch.jsonを編集
setlocal enabledelayedexpansion

set TARGET_FILENAME=launch.json
echo %TARGET_FILENAME%を更新をしています

set INPUT_FILE=.vscode\%TARGET_FILENAME%
set OUTPUT_FILE=.vscode\new_launch.json
for /f "delims=" %%a in (%INPUT_FILE%) do (
set line=%%a
echo !line:${ProjectName}=%DIR_NAME%!>>%OUTPUT_FILE%
)

echo %INPUT_FILE%を削除します。
del %INPUT_FILE%
if %errorlevel% == 0 (
    echo %INPUT_FILE%削除に成功しました
) else (
    echo %INPUT_FILE%削除に失敗しました
    pause
    exit /B -1
)

echo %OUTPUT_FILE%を%INPUT_FILE%にします。
rename %OUTPUT_FILE% %TARGET_FILENAME%
if %errorlevel% == 0 (
    echo %INPUT_FILE%作成に成功しました
) else (
    echo %INPUT_FILE%作成に失敗しました
    pause
    exit /B -1
)

REM settings.jsonを編集

set TARGET_FILENAME=settings.json
echo %TARGET_FILENAME%を更新をしています

set INPUT_FILE=.vscode\%TARGET_FILENAME%
set OUTPUT_FILE=.vscode\new_settings.json
for /f "delims=" %%a in (%INPUT_FILE%) do (
set line=%%a
echo !line:${ProjectFullPath}=%VSCODE_PROJECT_DIR_FULLPATH%!>>%OUTPUT_FILE%
)

echo %INPUT_FILE%を削除します。
del %INPUT_FILE%
if %errorlevel% == 0 (
    echo %INPUT_FILE%削除に成功しました
) else (
    echo %INPUT_FILE%削除に失敗しました
    pause
    exit /B -1
)

echo %OUTPUT_FILE%を%INPUT_FILE%にします。
rename %OUTPUT_FILE% %TARGET_FILENAME%
if %errorlevel% == 0 (
    echo %INPUT_FILE%作成に成功しました
) else (
    echo %INPUT_FILE%作成に失敗しました
    pause
    exit /B -1
)

endlocal

echo 新規プロジェクト[%DIR_NAME%]を作成しました。
endlocal

pause
exit /B 0

