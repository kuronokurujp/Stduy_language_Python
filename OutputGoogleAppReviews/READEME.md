# OutputGoogleAppReviewsのレビュー一覧を取得して出力

## 免責事項

このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

## 開発環境
- [SeriAPI](https://serpapi.com/)を利用
    1. アカウントを作成
    1. [APIキーサイト](https://serpapi.com/manage-api-key)のYour Private API Key項目の下にあるキー文字列をコピー
    1. conifgファイルをコピーして.configというファイル名に変えてペースト
    1. .configファイルのapi_keyにコピーしたPrivateAPIKeyをペースト

## 目的
- グーグルプレイストアで配信しているアプリ評価を分析するためにレビュー情報を取得するツールを作成

## 注意点
- SeriAPIは無料枠でデータの取得回数が月100回まで
