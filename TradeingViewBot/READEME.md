# トレーディングビューのbot

# 開発環境

- windows10
- python3.10
- [ngrok](https://ngrok.com/)
- [wxFormBuilder](https://github.com/wxFormBuilder/wxFormBuilder)
    - UIをGUIで作成に利用


## 目的
- [トレーディングビュー](https://jp.tradingview.com/)のアラート通知を取得して処理するbot
- アラート通知を取得したら注文処理をする
    - 注文処理は独自実装
        - 楽天RSSの注文を行える(予定)

## 参考サイト
- [GUIクライアントをwxPythonで作成](https://zero-cheese.com/6667/)
- [GUIクライアントをFletで作成](https://qiita.com/NasuPanda/items/48849d7f925784d6b6a0)
- [トレーディングビューのアラート通知を受け取る](https://note.com/mioka_/n/n62b2615ca1cc)
- [ngrokを使ったローカルサーバー構築](https://zenn.dev/yu1low/articles/459fc8023e80a2)
- [log処理の実装方法](https://qiita.com/FukuharaYohei/items/92795107032c8c0bfd19)
- [ディレクトリ内のファイル探索](https://note.nkmk.me/python-pathlib-iterdir-glob/)
- [pathlibモジュールを使ったファイル削除](https://www.javadrive.jp/python/file/index10.html)
- [tomlファイルでファイルパスはシングルクォートで(tomlフォーマット説明が日本語)](https://toml.io/ja/v0.5.0)
- [tmolファイルのロード方法](https://qiita.com/tetrapod117/items/d27388d5ed9386c1efd6)
- [ngrokを扱えるpythonモジュール](https://ngrok.github.io/ngrok-python/index.html)
- [HttpServerクラスのserver_foreverを別スレッドにしてブロック状態にしない方法(Asynchronous Mixins項目に注目)](https://docs.python.org/3/library/socketserver.html)
- [webhookの送信テストコード](https://laboratory.kazuuu.net/sending-a-webhook-using-request-in-python/)
- [PythonでVBAのメソッドを呼ぶ方法](https://fastclassinfo.com/entry/run_excelvba_from_python/)
- [wxPythonのUIをGUIツールで作成](https://zenn.dev/naonaorange/articles/20190815_wxpython_wxformbuilder)
