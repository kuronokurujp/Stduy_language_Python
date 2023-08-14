# Stduy_language_Python

Sample Python List

# 説明
- プログラミング言語Pythonの学習用

# 免責事項 
このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

# 開発環境構築

## Pytnon のインストール

-   win 版
    1. vscode を開く
    1. ctrl + `でターミナルを開いて移動する
    1. 以下のコマンドを実行
        > python
    1. python が入っていないと MicrosoftStore が開いて python のダウンロード画面を出すのでダウンロードする
-   参考サイト
    -   [Python+VSCode におすすめの拡張機能](https://qiita.com/momotar47279337/items/73157407ae824751afc4)

## venv などの仮想環境を動かすための準備

    -   win 版

        -   仮想環境を動かすため PowerShell の ps ファイルを実行するものがある
        -   しかし PowerShell の環境によっては ps ファイルを実行不可能な設定なのもある

            -   .\venv\Scripts\activete を実行すると以下のエラーが出た
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
        -   以下のコマンドで作成
            -   python -m venv venv

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

    -   以下のコマンドで mypy をインストール
        pip install mypy
    -   設定画面の mypy の利用を有効化する

        -   グローバル設定ファイル settgins.json に以下の記述を追加
            "python.linting.mypyEnabled": true

    -   関数を作成した動作確認

        -   以下のコードを添付して hello(123)の箇所でエラーが表示しているなら成功
            def hello(name: str) -> str:
            return "Hello " + name

        result: str = hello(123)

    -   メモ
        -   pyfields のパッケージを使うと正しいコードを記述しているのにその箇所がエラーとなっていた
            -   つまり不十分！
        -   クラスのメソッドで戻り値の型ヒントを付けているメソッドをエラーとしていた。
        -   これは利用しない方がいいと判断した
        -   導入が簡単だから入れたが、失敗だった
    -   参考サイト
        [mypy を VS code で使うための手順](https://yoshitaku-jp.hatenablog.com/entry/2020/12/28/130000)

## フォーマットに合わせてコード整形する環境作成

-   win 版

    -   以下のコマンドで black をインストール
        pip instlal black
    -   VSCode で Black を使うように設定

        -   グローバル設定ファイル settgins.json に以下の記述を追加
            "python.formatting.provider": "black"

    -   alt + shift + f のショートカットキーでコード整形を実行
        -   Black で整形するための拡張機能がなけらばインストールを要求するのでその場合はインストール
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
    1. 作成したディレクトリに__init__.pyを作成
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

-   参考サイト
    -   [pytest でのインストールについて分かった](https://rurukblog.com/post/vscode-pytest/)

### pytest の collect-only コマンドからテストするように足りないパッケージを教えてくれる

1.  以下のコマンドを実行

    -   pytest collect-only
        -   テストできるパッケージについての情報など一覧が出る

-   参考サイト
    -   [【VSCode】Pytest Discovery Error : Error discovering](https://rurukblog.com/post/Pytest-Discovery-Error/)

### pytest を使ったコードデバッグ方法

-   参考サイト
    -   [pytest のコードでのデバッグ方法](https://rurukblog.com/post/vscode-pytest/)

## 実行で参考にしたサイト

-   [コマンドツールのエラーコード出力方法](https://yaromai.jp/python-exit/)
-   [Json の制御](https://qiita.com/Morio/items/7538a939cc441367070d)
-   [LF(ラインフィールド)という改行コードについて](https://hk29.hatenablog.jp/entry/2020/12/24/225735#:~:text=Python%20%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89LF%E3%81%AE%E3%83%86%E3%82%AD%E3%82%B9%E3%83%88%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E4%BD%9C%E6%88%90%E3%81%99%E3%82%8B%20Python%20%E6%AC%A1%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%80%81newline%3D%22n%22%E3%82%92%E5%85%A5%E3%82%8C%E3%81%BE%E3%81%99%E3%80%82%20with%20open%20%28%27test_LF.tsv%27%2C%20%27w%27%2C,newline%3D%20%22n%22%29%20as%20f%3A%20%E3%81%99%E3%82%8B%E3%81%A8%E3%80%81%E4%B8%8B%E5%9B%B3%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89%E3%82%92LF%EF%BC%88%E3%83%A9%E3%82%A4%E3%83%B3%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%EF%BC%89%E3%81%A7%E4%BD%9C%E6%88%90%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82%20newline%3D%22n%22%E3%82%92%E5%85%A5%E3%82%8C%E3%81%AA%E3%81%84%E5%A0%B4%E5%90%88%E3%81%AF%E3%80%81%E4%B8%8B%E5%9B%B3%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E6%94%B9%E8%A1%8C%E3%82%B3%E3%83%BC%E3%83%89%E3%81%AFCRLF%E3%81%AB%E3%81%AA%E3%82%8A%E3%81%BE%E3%81%99%EF%BC%88%20Windows%20%E3%81%AE%E5%A0%B4%E5%90%88%EF%BC%89)
-   [Ctrl + /で範囲選択したコードを一括コメントアウト出来る！](https://1978works.com/2022/09/18/how-to-comment-out-a-block-in-python-by-using-keybordshort-cut-in-visual-studio-code/#:~:text=%E3%81%9D%E3%81%93%E3%81%A7%E3%80%81VSCode%E3%81%8C%E6%8F%90%E4%BE%9B%E3%81%99%E3%82%8B%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%89%E3%82%B7%E3%83%A7%E3%83%BC%E3%83%88%E3%82%AB%E3%83%83%E3%83%88%E3%82%92%E4%BD%BF%E3%81%84%E3%81%BE%E3%81%97%E3%82%87%E3%81%86%E3%80%82%20%E4%B8%8B%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E7%B0%A1%E5%8D%98%E3%81%AB%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82%20%E3%81%82%E3%82%8B%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%85%A8%E4%BD%93%E3%82%92%E4%B8%80%E5%BA%A6%E3%81%AB%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%A2%E3%82%A6%E3%83%88%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95%EF%BC%9A%E3%80%8CCtrl%E3%80%8D%EF%BC%8B%E3%80%8C%2F%E3%80%8D%20fig1%20%E3%81%BE%E3%81%9A%E4%B8%8A%E7%94%BB%E5%83%8F%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%82%B3%E3%83%A1%E3%83%B3%E3%83%88%E3%82%A2%E3%82%A6%E3%83%88%E3%81%97%E3%81%9F%E3%81%84%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E5%85%A8%E4%BD%93%E3%82%92%E9%81%B8%E6%8A%9E%E3%81%97%E3%81%BE%E3%81%99%E3%80%82,%E3%81%9D%E3%81%97%E3%81%A6%E3%81%9D%E3%81%AE%E3%81%BE%E3%81%BE%E3%81%A7%E3%80%81%E3%82%AD%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%89%E3%81%A7%E3%80%8CCtrl%E3%80%8D%E3%83%9C%E3%82%BF%E3%83%B3%E3%81%A8%E3%80%8C%2F%E3%80%8D%E3%83%9C%E3%82%BF%E3%83%B3%E3%82%92%E5%90%8C%E6%99%82%E3%81%AB%E6%8A%BC%E3%81%97%E3%81%A6%E3%81%8F%E3%81%A0%E3%81%95%E3%81%84%E3%80%82%20fig2%20%E3%81%99%E3%82%8B%E3%81%A8%E3%81%93%E3%81%AE%E7%94%BB%E5%83%8Ffig2%E3%81%AE%E3%82%88%E3%81%86%E3%81%AB%E3%80%81%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF%E3%81%AE%E3%81%99%E3%81%B9%E3%81%A6%E3%81%AE%E8%A1%8C%E3%81%AB%20%E3%80%8C%23%E3%80%8D%E3%81%A8%E3%81%9D%E3%81%AE%E7%9B%B4%E5%BE%8C%E3%81%AB%E3%80%8C%E5%8D%8A%E8%A7%92%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%80%8D%20%E3%81%A8%E3%81%8C%E8%87%AA%E5%8B%95%E7%9A%84%E3%81%AB%E4%B8%80%E6%B0%97%E3%81%AB%E5%85%A5%E5%8A%9B%E3%81%A7%E3%81%8D%E3%81%BE%E3%81%99%E3%80%82)
-   [config.ini で%%で囲ったテキストの取得方法](https://stackoverflow.com/questions/71854527/configparser-interpolationsyntaxerror-must-be-followed-by-or-found#:~:text=Python%20treats%20the%20%25%20character%20differently%2C%20when%20part,to%20obfuscate%20plain%20text%20passwords%20from%20prying%20eyes%21)
    -   %%と二重にすると良い
-   [config.ini にリストや辞書の要素を対応する方法](https://stackoverflow.com/questions/335695/lists-in-configparser)
-   [クラスの変数の検証が出来るパッケージについて](https://dev.classmethod.jp/articles/python_class_instance_validation/)
-   拡張について
