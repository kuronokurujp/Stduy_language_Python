# バッチファイル一覧

## 説明

単純作業を自動化したバッチファイル一覧

## 免責事項

このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

## バッチ一覧

-   MakeProject.bat
    -   Python 開発プロジェクトを新規作成
    -   コマンドプロンプトの対話形式
    -   必要環境
        |OS|ツール ①|ツール ②|
        |----|----|----|
        |Windows10/11|[pyenv](https://zenn.dev/takuya_zenn/articles/4204dadc1bbdd7)|[vscode](https://codezine.jp/article/detail/16467)|
    -   利用前準備
        1. vscode ディレクトリをコピーして.vscode に名前を変えてペースト
        1. コピーした.vscode ディレクトリの以下のファイルは個人環境に合わせて修正してほしい
            - launch.json
            - settings.json
                - cornflask.linter.executablePath の項目は変更してはいけない

## 参考サイト

-   [コマンド入力と入力検証](https://web-creators-hub.com/windows/bat-set-s/)
-   [ファイル削除](https://ribbit.konomi.app/cmd/commands/del/)
    -   ファイルパスは/で区切るとエラーになった
    -   \で区切ると成功した
-   [変数の中身を置換](https://qiita.com/miriwo/items/8bff151f82839e8c45a4)
    -   パス区切りを\から/に変更するのに置換で利用
-   [ファイル名変更](https://www.javadrive.jp/command/file/index3.html)
    -   第二引数には変更したいファイル名のみ指定
    -   第二引数にパスを入れるとエラーになる
-   [テキストファイル内で指定文字列を置換](https://qiita.com/yacchi1123/items/97e75c6784b5b507f701)
    -   vscode の.vscode にある json ファイルの一部を置換するために利用
-   [バッチファイル入門](https://www.tohoho-web.com/ex/bat.html#set)
