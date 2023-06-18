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

