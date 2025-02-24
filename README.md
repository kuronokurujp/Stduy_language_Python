# Stduy_language_Python

Sample Python List

## 説明

-   プログラミング言語 Python の学習用
-   Python 開発経験値を身に着けるためにツール/ゲーム/ Web サイトなど作成したアプリ一覧

## 免責事項

このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

# 利用ツール

| ツール     |
| ---------- |
| pyenv      |
| Chocolatey |
| VSCode     |

# 開発環境構築

## Pytnon のインストール

-   win 版
    -   pyenv をインストールする方法
        1. windows 用のパッケージ管理ソフト「Chocolatey」を導入
            - 以下のサイトを参考にしてインストールした
            - [Chocolatey の導入方法](https://zenn.dev/kazuma_r5/articles/a6d2608446ebdf/)
        1. Chocolate を使って pyenv をインストール
            - 以下のサイトの項目「pyenv インストール」を参考にしてインストールした
            - [Windows に pyenv を導入する方法](https://zenn.dev/kazuma_r5/articles/a6d2608446ebdf)
        1. pyenv がインストールか確認
            - PowerShell を開いて以下のコマンドを実行
                - pyenv --version
                - 実行すると以下のメッセージがでる可能性がある
                    - pyenv : このシステムではスクリプトの実行が無効になっているため...
                - このメッセージは PowerShell のポリシー設定が原因なので以下のサイトを参考にして解決できた
                    - [「このシステムではスクリプトの実行が無効になっているため～～～を読み込むことができません」の対処法【Windows】](https://nishikiout.hatenablog.com/entry/2023/03/08/012215)
    -   参考サイト
        -   [pyenv 利用のまとめ](https://qiita.com/m3y/items/45c7be319e401b24fca8)

## venv などの仮想環境を動かすための準備

-   win 版

    -   仮想環境を動かすため PowerShell の ps ファイルを実行するものがある
    -   しかし PowerShell の環境によっては ps ファイルを実行不可能な設定なのもある

        -   .\venv\Scripts\activate を実行すると以下のエラーが出た
            ..\venv\Scripts\Activate.ps1 を読み込むことができません。
        -   原因 1: PowerShell の安全装置の一つであるスクリプト不許可の設定がされている

            -   どういう事か
                -   PowerShell の安全装置の一つであるスクリプト不許可の設定がされている
            -   原因なのかどうかの確認方法

                1. PowerShell を実行
                1. Get-ExecutionPolicy コマンドを実行
                1. Restricted が表示されたら原因１に該当

            -   原因対策

                1. PowerShell を管理者として実行
                1. 以下のコマンドを実行して Y を入力
                   set-executionpolicy remotesigned

                1. Get-ExecutionPolicy コマンドを実行
                1. RemoteSigned が表示されたら OK

            -   参考サイト
                -   [「このシステムではスクリプトの実行が無効になっているため、ファイル XXX を読み込みことができません」エラー（PowerShell）が出る原因と対処方法](https://rainbow-engine.com/ps-script-execution-disabled/)

## 仮想環境作成

-   win 版

    -   pyenv が入っている場合

        -   [参考にしたサイト](https://zenn.dev/sion_pn/articles/4418eeda7c62d0)

        1. 利用する python をインストールする
            - pyenv install xxx
                - xxx にインストールしたい python のバージョンを指定
                - インストールできるバージョンのリストは以下のコマンドで出力できる
                    - pyenv install --list
        1. プロジェクトディレクトリに移動
        1. プロジェクトで利用する python のバージョンを設定
            - pyenv local xxx
            - インストール済みバージョン一覧は以下のコマンドで出力できる
                - pyenv versions
        1. プロジェクトディレクトリに.python-version ファイルが作成しているかチェック
        1. .python-version ファイルは git にコミットしないように無視リストに追加

-   以下のコマンドで環境作成 - python -m venv venv

## 仮想環境有効

-   win 版
    -   仮想環境を作成したディレクトリに移動して以下のコマンドを実行
        -   .\venv\Scripts\activate

## 仮想環境無効

-   win 版
    -   以下のコマンド実行
        -   deactivate

## デバッグツールの環境作成

-   win 版

    -   以下のプロジェクトのディレクトリ構成を元に説明

        -   Project
            -   .vscode/
            -   venv/
            -   main.py

        1. .vscode/に settings.json ファイルを追加
        1. setting.json ファイルに以下の内容を記述して保存
           {
           "python.venvPath": "../venv",
           "python.pythonPath": "../venv"
           }

            python の path に python.exe があるパスを指定
            venv ディレクトリは setting.json がおいているディレクトリの一つ上においているので
            相対パス設定の"../venv"でうまくいく

        1. launch.json に環境変数 PYTHONPATH を設定する

            - これを設定しないと自作したモジュールをインポートしてもパスが通っていないからデバッグした時にインポートでエラーとなる

            1. launch.json を作成
            1. "configurations"項目に"env"項目を追加
            1. 環境変数"PYTHONPAT"を通す

                - こんな感じ

                    launch.json
                    ↓
                    {
                    // IntelliSense を使用して利用可能な属性を学べます。
                    // 既存の属性の説明をホバーして表示します。
                    // 詳細情報は次を確認してください: https://go.microsoft.com/fwlink/?linkid=830387
                    "version": "0.2.0",
                    "configurations": [
                    {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": true,
                    // 自作モジュールをアクティブにしているファイルからでも実行できるようにするためパスを通している
                    "env": {
                    "PYTHONPATH": "${workspaceFolder}"
                    }
                    }
                    ]
                    }

                - 参考サイト
                  [Visual Studio Code で Python デバッグ実行](https://www.yasunaga-lab.bio.kyutech.ac.jp/EosJ/index.php/Visual_Studio_Code%E3%81%A7Python%E3%83%87%E3%83%90%E3%83%83%E3%82%B0%E5%AE%9F%E8%A1%8C)

        1. デバッグ実行してブレークポイントで動くかチェック
            - ちなみに F5 キーでデバッグ実行！
            - launch.json がなければ生成する

    -   参考サイト
        -   [Python の仮想環境を VSCODE でデバッグできるようにする](https://zenn.dev/kokota/articles/fac6f6883afd4c)

## コードチェックのツール mypy の環境作成

-   win 版
    -   flake8
        -   以下のコマンドで flake8 をインストール
            pip install flake8
        -   flake8 を利用する拡張機能を追加
            -   [cornflakes-linter](https://marketplace.visualstudio.com/items?itemName=kevinglasson.cornflakes-linter)
        -   flake8 の設定ファイル tox.ini ファイルをワークススペースのトップディレクトリに配置
            -   tox.ini ファイルに flake8 のオプションを記述できる
                [flake8 のオプション一覧](https://flake8.pycqa.org/en/latest/user/options.html#top)
        -   vscode ワークスペースの設定
            -   .vscode/setting.json を作成
            -   setting.json に下記の記述を追加
                // flake8 の設定
                // 絶対パスでないと機能しない
                "cornflakes.linter.executablePath": "インストールした flake8.exe の絶対パス(相対パスだとだめだった)",
                // lint を有効
                "python.linting.enabled": true,
                // デフォルトの lint セーブは無効
                "python.linting.lintOnSave": false,
                // 初期状態の pylint は無効
                "python.linting.pylintEnabled": false,
                // デフォルトの flake8 は無効
                "python.linting.flake8Enabled": false,
        -   メモ
            -   ファイルを開かないと問題点が表示しない
            -   全ファイルを問題点を出すには flake8 ./ をターミナルに打てばカレントディレクトリ内にすべての py ファイルをチェックできた
        -   参考サイト
            [VSCode での Python 開発でリアルタイムにコードチェックが走るようにする](https://qiita.com/sakusaku_tempura/items/573e0a6e40bfc1960fd4)

## フォーマットに合わせてコード整形する環境作成

-   win 版

    -   以下のコマンドで black をインストール
        pip install black
    -   VSCode で Black を使うように設定

        -   グローバル設定ファイル settgins.json に以下の記述を追加
            "python.formatting.provider": "black"

    -   alt + shift + f のショートカットキーでコード整形を実行
        -   Black で整形するための拡張機能がなければインストールを要求するのでその場合はインストール
    -   コードが整形されていたら成功

    -   参考サイト
        -   [Black できれいに自動整形！flake8 と Black 導入と実行](https://qiita.com/tsu_0514/items/2d52c7bf79cd62d4af4a)

## コード補間の環境作成

-   [これを見てやってくれ！](https://qiita.com/Sunrise98/items/af866502b06165c3ae40)

## 単体テストの環境構築

1. pytest を利用
    - pip でインストール
        - pip install pytest
1. tests ディレクトリを作成
    1. 作成したディレクトリに\***\*init**.py\*\* を作成
        - これを作成しないと自作パッケージのインポートでうまくいかずテストが実行できない
1. py ファイルを作成
    - test_xxx の関数を作成する
        - 関数名に test と頭につけないとテスト対象として認識されない
1. テストするコードを記述したり、テストする自作モジュールをインポートする
1. テスト用の py ファイルを開くとアクティブバーにテストアイコンが出るのでクリック
1. テスト用の環境作りますかというボタンがあるのでボタンを押す
1. settings.js に tests ディレクトリのパスを指定
   こんな感じ(cli_simple ディレクトリ中にあるテストコードが入っている tests ディレクトリを指定)
   "${workspaceFolder}/cli_simple/tests",
1. test_xxx.py というテスト用の py ファイルを作成
    - **test.py というファイルではテストフレームワークで認識しないので注意**

-   参考サイト
    -   [pytest でのインストールについて分かった](https://rurukblog.com/post/vscode-pytest/)

## pip パッケージ管理環境構築

### pip でインストールしたパッケージを一括で更新したりするケースがあるから

1. [pip-review](https://github.com/jgonggrijp/pip-review)を利用
    - pip でインストール
        - pip install pip-review

-   参考サイト
    -   [Python と pip パッケージのバージョン確認＆一括アップデート方法](https://zenn.dev/haretokidoki/articles/8836fecf6b4cfc)

### pytest の collect-only コマンドからテストするように足りないパッケージを教えてくれる

1.  以下のコマンドを実行

    -   pytest collect-only
        -   テストできるパッケージについての情報など一覧が出る

-   参考サイト
    -   [【VSCode】Pytest Discovery Error : Error discovering](https://rurukblog.com/post/Pytest-Discovery-Error/)

### pytest を使ったコードデバッグ方法

-   参考サイト
    -   [pytest のコードでのデバッグ方法](https://rurukblog.com/post/vscode-pytest/)

### pip でインストールしたパッケージ一覧をエクスポートとインポート方法

-   エクスポート方法

    -   以下のコマンドでインストールしたパッケージ一覧を記載したファイルをエクスポートできる
        pip freeze > requirements.txt

-   インポート方法
    -   以下のコマンドで requirements.txt に記載したパッケージ一覧をインポートできる
        pip install -r requirements.txt

## 単純作業をシェル or バッチファイルで自動化

-   Shell ディレクトリにまとめている
    -   Python プロジェクトの自動作成バッチファイルがある

## Django

### ローカライズ対応

-   以下のサイトをまず参考にした
    -   https://blog.narito.ninja/detail/86/
    -   項目[翻訳ファイルの作成]の前まではそのまま使えた
        -   django-admin makemessages -l ja
        -   上記のコマンドを実行したら以下のエラーが出た
            -   Django makemessages command generates error: "xgettext: Non-ASCII string"
        -   これのサイト以外のを参考にした
-   次はこのサイトが参考になった
    -   https://sinyblog.com/django/translation-001/
    -   項目[メッセージファイルの作成]の以下のコマンドでメッセージを作成してみた
        -   python manage.py makemessages -l ja
        -   しかしエラーになった
            -   ImportError: cannot import name ‘ugettext_lazy’ from ‘django.utils.translation’
        -   インポートがないというエラーで調査した
            -   以下のサイトで解決した
                -   https://forum.djangoproject.com/t/importerror-cannot-import-name-ugettext-lazy-from-django-utils-translation/10943
            -   参考にしたサイトは django3 系のようだ
                -   試した環境が django4 系だと 3 系のインポートファイルがなくなったみたい
            -   利用できるインポートに変えてうまくいった
        -   もう一度以下のコマンドを実行
            -   python manage.py makemessages -l ja
        -   しかしエラーになった
            -   Django makemessages command generates error: "xgettext: Non-ASCII string"
            -   最初に参考にしたサイトで試したエラーが起きた
        -   調査したら以下のサイトを参考にして解決出来た
            -   https://stackoverflow.com/questions/45078011/django-makemessages-command-generates-error-xgettext-non-ascii-string
            -   venv の仮想環境での実行が原因のようだ
            -   以下のコマンドで成功した
                -   python manage.py makemessages -l ja -i venv
    -   使える状態になった
-   ローカライズテキストの追加やコンパイルなど残り対応について
    -   以下のサイトの翻訳設定や言語コンパイルの項目で対応できる
        -   https://sinyblog.com/django/translation-001/

## 開発メモ

-   クラスの**dict**にはクラス変数定義の要素が入っているが、**init**内でクラス変数定義しないと要素が入らない

    -   **dict**が要素に入らないケース

              class Test(object):
                  value: int = 0

              test: Test = Test()
              # __dict__を出力しても空になっている
              print(test.__dict__)

    -   **dict**に要素が入るケース

             class Test(object):
                 def __init__(self):
                     self.value = 0

             test: Test = Test()
             # __dict__を出力するとvalue要素がある
             print(test.__dict__)

-   static ディレクトリは各アプリディレクト内で作成しないといけない
    -   django で js ファイルを配置したかったので以下のサイトを参考にした
        -   https://di-acc2.com/programming/python/20081/
    -   この通りにやったのだが、js ファイルが読み込まれなかった
    -   次に以下のサイトを参考にした
        -   https://www.geeksforgeeks.org/django-static-file/
    -   アプリディレクトリに static ディレクトリを作成してその中に js ファイルを配置した
    -   このやり方だとうまくいった
    -   static ディレクトリはアプリディレクトリで作成しないだめみたい
    -   利用できる static ディレクトリを調べるコマンドがある
        -   python.exe .\manage.py findstatic .
        -   これで現在利用できる static ディレクトリ一覧が表示する
            -   [参考サイト](https://qiita.com/okoppe8/items/38688fa9259f261c9440)

## 参考サイト

-   [コマンドツールのエラーコード出力方法](https://yaromai.jp/python-exit/)
-   [Json の制御](https://qiita.com/Morio/items/7538a939cc441367070d)
-   [LF(ラインフィールド)という改行コードについて](https://hk29.hatenablog.jp/entry/2020/12/24/225735#:~:text=Python%20%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89LF%E3%81%AE%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B%20Python%20%E6%AC%A1%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%80%81newline%3D%22n%22%E3%82%92%E5%85%A5%E3%82%8C%E3%81%BE%E3%81%99%E3%80%82%20with%20open%20%28%27test_LF.tsv%27%2C%20%27w%27%2C,newline%3D%20%22n%22%29%20as%20f%3A%20%E3%81%99%E3%82%8B%E3%81%A8%E3%80%81%E4%B8%8B%E5%9B%B3%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92LF%EF%BC%88%E3%83%A9%E3%82%A4%E3%83%B3%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%EF%BC%89%E3%81%A7%E4%BD%9C%E6%88%90%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82%20newline%3D%22n%22%E3%82%92%E5%85%A5%E3%82%8C%E3%81%AA%E3%81%84%E5%A0%B4%E5%90%88%E3%81%AF%E3%80%81%E4%B8%8B%E5%9B%B3%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89%E3%81%AFCRLF%E3%81%AB%E3%81%AA%E3%82%8A%E3%81%BE%E3%81%99%EF%BC%88%20Windows%20%E3%81%AE%E5%A0%B4%E5%90%88%EF%BC%89)
-   [Ctrl + /で範囲選択したコードを一括コメントアウト出来る！](https://1978works.com/2022/09/18/how-to-comment-out-a-block-in-python-by-using-keybordshort-cut-in-visual-studio-code/#:~:text=%E3%81%9D%E3%81%93%E3%81%A7%E3%80%81VSCode%E3%81%8C%E6%8F%90%E4%BE%9B%E3%81%99%E3%82%8B%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%89%E3%82%B7%E3%83%A7%E3%83%BC%E3%83%88%E3%82%AB%E3%83%83%E3%83%88%E3%82%92%E4%BD%BF%E3%81%84%E3%81%BE%E3%81%97%E3%82%87%E3%81%86%E3%80%82%20%E4%B8%8B%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E7%B0%A1%E5%8D%98%E3%81%AB%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82%20%E3%81%82%E3%82%8B%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%85%A8%E4%BD%93%E3%82%92%E4%B8%80%E5%BA%A6%E3%81%AB%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%A2%E3%82%A6%E3%83%88%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%EF%BC%9A%E3%80%8CCtrl%E3%80%8D%EF%BC%8B%E3%80%8C%2F%E3%80%8D%20fig1%20%E3%81%BE%E3%81%9A%E4%B8%8A%E7%94%BB%E5%83%8F%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%A2%E3%82%A6%E3%83%88%E3%81%97%E3%81%9F%E3%81%84%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%85%A8%E4%BD%93%E3%82%92%E9%81%B8%E6%8A%9E%E3%81%97%E3%81%BE%E3%81%99%E3%80%82,%E3%81%9D%E3%81%97%E3%81%A6%E3%81%9D%E3%81%AE%E3%81%BE%E3%81%BE%E3%81%A7%E3%80%81%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%89%E3%81%A7%E3%80%8CCtrl%E3%80%8D%E3%83%9C%E3%82%BF%E3%83%B3%E3%81%A8%E3%80%8C%2F%E3%80%8D%E3%83%9C%E3%82%BF%E3%83%B3%E3%82%92%E5%90%8C%E6%99%82%E3%81%AB%E6%8A%BC%E3%81%97%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84%E3%80%82%20fig2%20%E3%81%99%E3%82%8B%E3%81%A8%E3%81%93%E3%81%AE%E7%94%BB%E5%83%8Ffig2%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%80%81%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E3%81%AE%E3%81%99%E3%81%B9%E3%81%A6%E3%81%AE%E8%A1%8C%E3%81%AB%20%E3%80%8C%23%E3%80%8D%E3%81%A8%E3%81%9D%E3%81%AE%E7%9B%B4%E5%BE%8C%E3%81%AB%E3%80%8C%E5%8D%8A%E8%A7%92%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%80%8D%20%E3%81%A8%E3%81%8C%E8%87%AA%E5%8B%95%E7%9A%84%E3%81%AB%E4%B8%80%E6%B0%97%E3%81%AB%E5%85%A5%E5%8A%9B%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82)
-   [config.ini で%%で囲ったテキストの取得方法](https://stackoverflow.com/questions/71854527/configparser-interpolationsyntaxerror-must-be-followed-by-or-found#:~:text=Python%20treats%20the%20%25%20character%20differently%2C%20when%20part,to%20obfuscate%20plain%20text%20passwords%20from%20prying%20eyes%21)
    -   %%と二重にすると良い
-   [config.ini にリストや辞書の要素を対応する方法](https://stackoverflow.com/questions/335695/lists-in-configparser)
-   [クラスの変数の検証が出来るパッケージについて](https://dev.classmethod.jp/articles/python_class_instance_validation/)
