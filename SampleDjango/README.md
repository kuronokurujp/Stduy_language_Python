# WebフレームワークDjangoの機能テストサンプル

# 開発環境
windows10
python3.10

# 開発環境準備
- 開発用ディレクトリを作成
- ターミナルを起動して開発用ディレクトリをカレントディレクトリにする
- 仮想環境を作る
    - 作成コマンド
        python -m venv venv
- 作成した仮想環境を有効にする
    - 有効コマンド
        .\venv\Scripts\activate 
    - 参考サイト
        - https://zenn.dev/ryotoitoi/articles/0fd021ad9405bf
- pipの確認
    - 確認コマンド
        pip list
    - pipのアップグレードを要求するメッセージが出るのでアップグレードする
    - アップグレードコマンドはメッセージの中に含まれているのでそのコマンドを利用
    
- djangoをインストール
    - インストールコマンド
        pip install django==4.0.2
    - インストールしたdjangoのバージョン表示コマンド
        python -m django version
        
# プロジェクト作成
    - 以下のコマンドでプロジェクトを作成する
        django-admin starproject XXX .
        XXXはプロジェクト名
#  プロジェクトの環境設定
    - 言語を日本語 / タイムスタンプを日本に合わせる
    - setting.pyを開いて以下の項目を変更
        LANGUAGE_CODE = 'ja'
        TIME_ZONE = 'Asia/Tokyo'

# 開発環境の外部ファイル対応
    - .envファイルをプロジェクト直下に作る
    - .envファイルにsetting.pyのSECRET_KEYの行をコピーして張り付ける
    - .envファイルをロードするためのパッケージをインストール
        pip install python-dotenv
        
    - setting.pyで.envファイルをロードする
        import os
        from dotenv import load_dotenv
        
        load_dotenv(BASE_DIR / '.env')
        
        SECRET_KEY = os.getenv('SECRET_KEY')
        
# 利用しているパッケージ一覧のファイルを作成
    - これを作成しておくとデプロイする時に一緒にパッケージをインストールしてくれる
    - 一覧ファイルを作成
        pip freeze > requirements.txt
        
# pythonanywhereでデプロイする方法
    - pythonanywhereのAPIトークンを作成する
    - pythonanywhereのコンソールを開く
    - pythonanywhereのパッケージをインストール
        pip install --user pythonanywhere
    - コンソールでgithubのリポジトリから取得するコマンド
        pa_autoconfigure_django.py --python=3.10 gitのhttpsのurl --nuke
        
    - githubのプライベートリポジトリをcloneする方法
        - 以下のサイトを参考にSSHのキーを作成
            [SSH作成参考サイト](https://help.pythonanywhere.com/pages/ExternalVCS/)
            
        - ssh-keygenコマンドではファイル名など変えないのでそのままで良い
            - そうすれば作成したカレントディレクトリに.sshディレクトリが作成されてid_rsa.pubファイルが作成される。
        - cat ~/.ssh/id_rsa.pubを実行した出力したファイル内容をgithubに設定する
            - settings -> SSH and GPD keysを選択
            - "New SSH key"ボタンを押してcatコマンドで出力した出力内容をコピーする
        - リポジトリのcloneのSSHをコピーする
        - リポジトリをコマンドで取得する
            - pa_autoconfigure_django.py --python=3.10 コピーしたsshの文字列 --nuke
        
    - その他
        requirements.txtでパッケージをインストールしているが、
        パッケージが変わった場合はどうやって更新すればいいのか？
        
        pip install -r requrements.txt
        このコマンドで反映するしかないかも
        https://qiita.com/sakusaku12/items/21083c73c8afa4f6c78d

# gitでアップしてはいけない対象
    media
    .env
    migrations
        以下のpyファイル

