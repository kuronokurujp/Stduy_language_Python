# WebフレームワークDjangoのHelloWorld

# 開発環境
windows10
python3.10

# Djangoのプロジェクト生成
    - プロジェクト生成するディレクトリを作成
    - 作成したディレクトリに移動
    - Djangoのプロジェクト作成コマンドでひな型のプロジェクトを作成
        - Configというプロジェクトを作成↓
            django-admin startproject Config . 

# Djangoのプロジェクトを仮想サーバーで起動
- Djangoプロジェクトのmanage.pyを使って仮想サーバーでDjangoプロジェクトを起動
    - 起動コマンド
        - python manage.py runserver
- 起動したDjangoプロジェクトを確認
    -   ターミナルにStarting development servr at http://xxx.xxx.xxx:8000/ というメッセージがある. <br>
        http~の部分をプラウザのURL枠に設定したページを開く
 
# Djangoのプロジェクト内に新規アプリを作成
- 新規アプリ作成コマンドでアプリを作成
    - Appという名前のアプリを新規に作成
       python manage.py startapp App 

- 作成したアプリをプロジェクトに紐づける
    - プロジェクトの紐づけは手動で行う
    - setting.pyに追加
        - INSTALLED_APPSの配列に作成したアプリのAppConfigメソッドを設定
            - INSTALLED_APPSの要素追加の記述ルール
                'アプリのルートディレクトリ名.apps.アプリ名Config'
                最後のアプリ名Configはアプリのルートディレクトリにあるapps.pyに定義しているので迷ったらapps.pyを見て確認するのがいい

# ページ起動時に作成したアプリへ遷移する設定
    - 作成したアプリのルートディレクトリのviews.pyを開く
    - アプリページ起動メソッドを作成
        - 追加内容
            from django.http import HttpResponse

            # 起動メソッド
            def index(response):
                return HttpResponse("Hello World")

    - urls.pyのINSTALLED_APPS配列にアプリページ起動メソッドを登録
        from App.views import index
        urlpatterns = [
            path('', index),
        ]