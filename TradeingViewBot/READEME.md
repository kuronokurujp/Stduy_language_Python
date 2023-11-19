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

## 免責事項

このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

## 参考サイト
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
- [抽象クラスの作成方法](https://qiita.com/TrashBoxx/items/7a76e46122191529c526)
- [PySimpleGUIのデモプログラム](https://github.com/PySimpleGUI/PySimpleGUI/tree/master/DemoPrograms)
- [GUIDの作成方法](https://stackoverflow.com/questions/3530294/how-to-generate-unique-64-bits-integers-from-python)
- [PySimpleGUIのTableの指定列を表示設定](https://serverarekore.blogspot.com/2021/12/pysimplegui.html)
