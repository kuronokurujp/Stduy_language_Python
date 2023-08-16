# Python の Web フレームワーク Django で作成した Todo プロジェクト

# 説明

Todo アプリを作成時の情報を記載しています。
Django による共通機能による説明は省いています。

# 開発環境

windows10
python3.10.11

## Todo リストビューの作成

-   views.py に ListView を継承したクラスを追加
    こんなコード
    from django.views.generic import ListView
    from App.models import Task

          class TodoListView(ListView):
              model = Task

-   urls.py に ListView を継承したクラスを設定

    -   urls.py の urlpatterns 配列に直接 View を設定する方法は使わず、コメントに記載"Including another URLconf"の方法を採用する
        -   url をアプリ毎に別途管理したいから
    -   アプリのディレクトリに urls.py を追加
    -   追加した urls.py に ListView を継承したクラスを登録
        コードはこんな感じ
        from django.urls import path
        from App.views import TodoListView

        urlpatterns = [
        path('', TodoListView.as_view(), name='task_list'),
        ]

-   view 用の html ファイルを追加

    -   アプリディレクトリの下に templates ディレクトリを追加
    -   追加した templates ディレクトリに Task ディレクトリを追加
    -   Task ディレクトリに TaskList.html を追加

-   追加した TaskList.html と view を紐づけ
    -   views.py を開く
    -   ListView を継承したクラスの template_name プロパティに TaskList.html のパスを設定
        こんな感じ
        class TodoListView(ListView): # templates ディレクトリの Task ディレクトリ内にある TaskList.html をテンプレートとする
        template_name = 'Task/TaskList.html'

# Task の詳細ビューを追加

-   詳細ビューのクラスを作る

    -   views.py を開く
    -   DetailView クラスを継承したクラスを宣言
        コード
        from django.views.generic import ListView, DetailView
        from App.models import Task

              # Todo詳細ビュー
              class TodoDetailView(DetailView):
                  model = Task
                  template_name = 'Task/TaskDetail.html'

    -   詳細ビューを遷移できるように登録

        -   urls.py を開く
        -   urlpatterns 配列に登録
            コード
            from App.views import TodoListView, TodoDetailView

                  urlpatterns = [
                      # タスク情報のid値をurlに含める
                      path('Task/<int:pk>', TodoDetailView.as_view(), name='task_detail'),
                  ]

            -   url に Task の Id を設定させてページ移動すると Task リストにある id のデータを使ったページが開く

    -   詳細ビューの html ファイルを新規追加
        -   templates ディレクトリに詳細ビュー用の html ファイルを追加
            -   名前は TaskDetail.html にしている
    -   TaskDetail.html に Task クラスのプロパティを表示するようにコード追加
        コード
        <h2>{{ task.title }}</h2>
        <p>{{ task.description }}</p>
        <p>{{ task.deadline }}</p>

# Todo の新規データ作成

    - データ入力ビューの追加
        - views.pyを開く
        - CreateViewクラスを継承した入力ビューのクラスを作成
            コード
                from django.views.generic import ListView, DetailView, CreateView
                from django.urls import reverse_lazy

                # Todo作成ビュー
                class TodoCreateView(CreateView):
                    model = Task
                    fields = '__all__'
                    template_name = 'Task/TaskForm.html'
                    success_url = reverse_lazy('task_list')

            - プロパティのfieldsがフォーム入力のフィールド
                - '__all__'とするとモデルの全てのフィールドが入力対象となる
            - プロパティのsuccess_urlにはデータ送信が成功した時に遷移するビュー先を指定
                reverse_lasyクラスにurls.pyのurlpattens配列に登録したビュークラスのプロパティnameで設定した文字列を指定
    - 入力ビューのurl登録
        - urls.pyを開く
        - 配列urlpatternsにビューを登録
            コード
            from App.views import TodoListView, TodoDetailView, TodoCreateView

            urlpatterns = [
                path('Task/New', TodoCreateView.as_view(), name='task_new'),
            ]

    - 入力ビュー用のhtmlファイルを新規追加
        - templatesディレクトリに入力ビュー用のhtmlファイルを追加
        - 追加したhtmlに入力フォームのコードを追加
            コード
            <form action="" method="POST">
                {% csrf_token %}
                <table>
                    {{ form.as_table }}
                </table>
                <input type="submit", value="送信"">
            </form>

            - 入力tableの前に必ず{% csrf_token %}を追加
                - これはwebページのセキュリティ対策
                - クロスサイトスクリプティング対策
                    - [クロスサイトスクリプティングとは](https://www.mobi-connect.net/blog/what-is-xss/)

## Todo の削除

    - データ削除ビューの追加
        - views.pyを開く
        - DeleteViewを継承した削除用ビュークラスを宣言
            - コード
                from django.views.generic import ListView, DetailView, CreateView, DeleteView
                # Todo削除ビュー
                class TodoDeleteView(DeleteView):
                    model = Task
                    template_name = 'Task/TaskDelete.html'
                    success_url = reverse_lazy('task_list')
    - 削除ビューをurl指定で遷移できるようにする
        - urls.pyを開く
        - urlpatterns配列に削除ビューを遷移できるように要素追加
            - urlにタスクのデータidを入れるようにする

            コード
            from django.urls import path
            from App.views import TodoDeleteView

            urlpatterns = [
                path('Task/<int:pk>/Delete', TodoDeleteView.as_view(), name='task_delete'),
            ]
    - 削除ビュー用のhtmlファイルを新規追加
        - templatesディレクトリにTaskDelete.htmlファイルを追加
        - 削除画面のhtmlを記述
            - urlに<int:pk>としているのでtask.pkでタスクidを取得できる
            コード
            <form action="" method="POST">
                {% csrf_token %}
                <h2>{{ task.pk }}.{{ task.title }}</h2>
                <p>このタスクを削除しても良いでしょうか？</p>
                <input type="submit", value="削除"">
            </form>

## Todo の更新

    - データ更新ビューの追加
        - views.pyを開く
        - UpdateViewを継承した更新用ビュークラスを宣言
            - コード
                # Todo編集ビュー
                class TodoUpdateView(UpdateView):
                    model = Task
                    fields = '__all__'
                    template_name = 'Task/TaskForm.html'
                    success_url = reverse_lazy('task_list')

    - データ更新ビューをurl指定で遷移できるようにする
        - urls.pyを開く
        - urlpatterns配列にデータ更新ビューを継承したクラスを追加
            - コード
                from django.urls import path

                from App.views import (
                    TodoUpdateView
                )

                urlpatterns = [
                    path('Task/<int:pk>/Edit', TodoUpdateView.as_view(), name='task_update'),
                ]

## プラウザページの見栄えを良くする

    - BootStrapを使う
        - 以下のサイトを参照
           https://getbootstrap.jp/docs/5.0/getting-started/introduction/

        - スターターテンプレートをコピー
        - TaskList.htmlにコピー
        - bodyタグ内に今まで記述したTaskList.htmlの内容を移動

    - 各テンプレートの共通コードを記述した拡張テンプレートを作成
        - templete/TaskのディレクトリにBase.htmlを作成
        - Base.htmlにBooststartpのスターターテンプレートをコピー
        - タグ<body>の直下にBase.htmlを組み込んだhtmlのコードを挿入するブロック文を組み込む
            コード
                <body>
                    {% block content %}
                    {% endblock content %}
                <body>
        - 各テンプレートのhtmlファイルにBase.htmlを組み込む
            コード
                <!-- 拡張してテンプレートのhtmlファイルを設定 -->
                {% extends 'Task/Base.html' %}
        - Base.htmlのブロックに置き換えるコードを記述
            - TaskList.htmlのコード
                <!-- 拡張してテンプレートのhtmlファイルを設定 -->
                {% extends 'Task/Base.html' %}

                <!-- 拡張テンプレートのhtmlに挿入するブロック内に個別コードを記述 -->
                {% block content %}

                  {% for task in object_list %}
                  <h3>
                      {{ task.title }}
                  </h3>
                  <h3>
                      {{ task.deadline }}
                  </h3>
                  {% endfor %}

                {% endblock content %}
        - 各ページの見た目を整える

# アカウントアプリの追加

    - 以下のコマンドでアカウントアプリを作成
        python manage.py startapp Accounts

    - Accountsディレクトリが作成されているかを確認
    - Configアプリのsettings.pyに作成したAcctounsアプリを追加
        コード
            INSTALLED_APPS = [
                ...
                'Accounts.apps.AccountsConfig'
            ]

    - Configのsettgins.pyにログインとログアウト先のURLを指定
        URLはurls.pyで設定したnameプロパティの文字列を指定する
        コード
            LOGIN_URL = 'login'
            LOGIN_REDIRECT_URL = 'task_list'
            LOGOUT_REDIRECT_URL = 'task_list'

## アカウントアプリにログインのビューを追加

    - views.pyにログイン用のViewクラスを作成
        コード
        from django.contrib.auth.views import LoginView

        class MyLoginView(LoginView):
            template_name = 'Accounts/Login.html'
            redirect_authenticated_user = True

## アカウントアプリの url にログインとログアウトのビューを追加

    - urls.pyにログインとログアウトのビューを追加
        - ログアウトのビューはdjangoで用意しているのを利用する
            コード
                from django.contrib.auth.views import LogoutView
                from Accounts.views import MyLoginView

                urlpatterns = [
                    path('login/', MyLoginView.as_view(), name='login'),
                    path('logout/', LogoutView.as_view(), name='logout'),
                ]

## ページにログインとログアウトの項目を追加

    - Base.htmlにログインとログアウトの項目を追加
        コード
            {% if user.is_authenticated %}
            <li class="nav-item">
              <a class="nav-link" href="{% url 'logout' %}">ログアウト</a>
            </li>
            {% else %}
            <li class="nav-item">
              <a class="nav-link" href="{% url 'login' %}">ログイン</a>
            </li>
            {% endif %}

        {% if user.is_autheticated %}
        この行でログインしている時としていない時の分岐ができる

## 各ページでログインしている時とログインしていない時で挙動を変える

    - ログアウトしている時はタスクの編集や削除ボタンなどを非表示にさせる
        {% if user.is_autheticated %}
        この行でログインかログアウトかを判断して表示内容を変える

## 会員登録を作る

    - 会員登録のビューをアカウントアプリに作成
        コード
            from django.views.generic import CreateView
            from django.contrib.auth.forms import UserCreationForm
            from django.urls import reverse_lazy

            class SignupView(CreateView):
                form_class = UserCreationForm
                template_name = 'Accounts/Singup.html'
                success_url = reverse_lazy('task_list')

    - 会員登録用のhtmlファイルを作成
        - Accounts/Singup.htmlを作成する
        - htmlの中身はAccounts/Login.htmlの内容をコピーで良い

    - アカウントアプリのurls.pyに会員登録のviewを設定
        コード
            from django.urls import path
            from Accounts.views import SignupView

            urlpatterns = [
                path('signup/', SignupView.as_view(), name='signup'),
            ]

    - Base.htmlに会員登録のボタンを追加
        コード
            <li class="nav-item">
              <a class="nav-link" href="{% url 'signup' %}">会員登録</a>
            </li>

            このコードはログアウト状態の時のみ表示
