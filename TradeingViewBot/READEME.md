# トレーディングビューのbot

# 開発環境

windows10
python3.10
ngrok

## 目的
- [トレーディングビュー](https://jp.tradingview.com/)のアラート通知を取得して処理するbot
- アラート通知を取得したら注文処理をする
    - 注文処理は独自実装
        - 楽天RSSの注文を行える(予定)

## 参考サイト
- [GUIクライアントをFletで作成](https://qiita.com/NasuPanda/items/48849d7f925784d6b6a0)
- [トレーディングビューのアラート通知を受け取る](https://note.com/mioka_/n/n62b2615ca1cc)
- [ngrokを使ったローカルサーバー構築](https://zenn.dev/yu1low/articles/459fc8023e80a2)
- [log処理の実装方法](https://qiita.com/FukuharaYohei/items/92795107032c8c0bfd19)
- [ディレクトリ内のファイル探索](https://note.nkmk.me/python-pathlib-iterdir-glob/)
- [pathlibモジュールを使ったファイル削除](https://www.javadrive.jp/python/file/index10.html)
