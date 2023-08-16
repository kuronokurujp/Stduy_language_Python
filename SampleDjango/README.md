# Web フレームワーク Django の機能テストサンプル

# 開発環境

windows10
python3.10

# 開発環境準備

-   開発用ディレクトリを作成
-   ターミナルを起動して開発用ディレクトリをカレントディレクトリにする
-   仮想環境を作る
    -   作成コマンド
        python -m venv venv
-   作成した仮想環境を有効にする
    -   有効コマンド
        .\venv\Scripts\activate
    -   参考サイト
        -   https://zenn.dev/ryotoitoi/articles/0fd021ad9405bf
-   pip の確認
    -   確認コマンド
        pip list
    -   pip のアップグレードを要求するメッセージが出るのでアップグレードする
    -   アップグレードコマンドはメッセージの中に含まれているのでそのコマンドを利用
-   django をインストール
    -   インストールコマンド
        pip install django==4.0.2
    -   インストールした django のバージョン表示コマンド
        python -m django version

# ファイルやディレクト名のルール

Django で生成で自動生成しているディレクトリの名前は先頭名が小文字になっている
合わせるためにはこちらが作成するディレクトリ名も先頭文字を小文字にするのがいいかも

# プロジェクト作成

    - 以下のコマンドでプロジェクトを作成する
        django-admin starproject XXX .
        XXXはプロジェクト名

        - 最後に.を付ける理由
            - .をつけないとConfigディレクトリが作成する
            - 作成したディレクトリに更にConfigディレクトリが作成されて入れ子になる
                - ディレクトリが以下の状態になる
                Root
                    - Config
                        - Config
                        - manage.py
            - .をつけると以下の状態になる
                - Root
                    -Config
                    -manage.py
            .をつければルートディレクトリ直下にConfigとmanage.pyが作成して入れ子状態ではなくなる
            最後の.はConfigを作成先の指定パス

# プロジェクトの環境設定

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

# Django のプロジェクト内に新規アプリを作成

-   新規アプリ作成コマンドでアプリを作成
    -   App という名前のアプリを新規に作成
        python manage.py startapp App

# 初期設定

-   作成したアプリの登録
    -   settings.py を開く
    -   INSTALLED_APPS にアプリ設定メソッドを追加
        -   INSTALLED_APPS = [
            'App.apps.AppConfig'
            ]

# DBにデータを保存するモデルクラスの作成
- 作成アプリのディレクトリにあるmodels.pyを開く
- クラスmodels.Modelを継承したクラスを宣言
- モデルのプロパティを宣言してDBに保存するフィールドと紐づける
    - こんな感じ
    class Task(models.Model):
        title = models.CharField(max_length=32)
        description = models.TextField(blank=True)
        deadline = models.DateField()
        
    - どんなフィールドクラスがあるかはドキュメントを見る
        - [フィールドクラスのドキュメント](https://docs.djangoproject.com/en/4.2/ref/models/fields/)
        - [Qiitaでまとめているフィールドクラス](https://qiita.com/nachashin/items/f768f0d437e0042dd4b3)

- 宣言モデルをマイグレーション対象とするマイグレートクラスを作成
    python manage.py makemigrations
    
- 作成したマイグレートクラスからマイグレーションする
    python manage.py migrate
    
    - 実行するとマイグレートクラスの処理が実行する
    - ターミナルに実行結果が表示されて全部OKと出ていると成功
    
- 管理画面用のスーパーユーザーを作成
    以下のコマンドで管理者アカウントを作成できる
        python manage.py createsuperuser

- 仮サーバーを起動して以下のURLで管理画面で移行
    http://127.0.0.1:8000/admin

- 管理画面に移動したら作成したスーパーユーザーでログインする
- 管理画面に作成したモデルを登録して管理画面からデータを追加できるようにする
    - admin.pyを開く
    - admin.site.registerメソッドでモデルを登録
        - こんな感じ
            from App.models import Task

            admin.site.register(Task)

    - 管理画面を更新して登録したモデルのデータが追加できているか確認

- 管理画面のデータ一覧の項目名を変える
    - モデル継承したクラスの__str__メソッドをオーバーライドする
    - オーバーライドした__str__メソッドに項目名を返す
        - こんな感じ
            def __str__(self):
                return self.title
    - 管理画面を更新してデータ一覧の項目名が変わっているかどうか確認


# 利用しているパッケージ一覧のファイルを作成

    - これを作成しておくとデプロイする時に一緒にパッケージをインストールしてくれる
    - 一覧ファイルを作成
        pip freeze > requirements.txt

# pythonanywhere でデプロイする方法

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

        pip install -r requirements.txt
        このコマンドで反映するしかないかも
        https://qiita.com/sakusaku12/items/21083c73c8afa4f6c78d

# git でアップしてはいけない対象

    media
    .env
    migrations
        以下のpyファイル
