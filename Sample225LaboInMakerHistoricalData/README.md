# サイト 225Labo から取得した日経先物 mini 過去データファイルからヒストリカルデータを作成ツール

## 概要

このツールは以下の事ができます

1. [225Labo の日経 225mini ダウンロードサイト](https://225labo.com/modules/downloads_data/index.php?cid=3)から取得した日経 225mini 過去データが入っているエクセルファイルを統合して 1 分足の ヒストリカルデータを csv ファイルで作成
1. 1.で作成した csv ファイルを使って 3 分足や 1 時間足のヒストリカルデータを csv ファイルで作成

## 免責事項

このソフトウェアの使用または使用不可によって、いかなる問題が生じた場合も、著作者はその責任を負いません。バージョンアップや不具合に対する対応の責任も負わないものとします。

## 開発環境

-   python 3.10.11
-   利用 python パッケージは requirements.txt を見てください
-   windows 10

## 利用前準備

-   [225Labo の日経 225mini ダウンロードサイト](https://225labo.com/modules/downloads_data/index.php?cid=3)から日経平均先物 225mini 銘柄の各データを取得します
-   取得データファイル名を修正します
    -   ファイル名にある年数のみにします
        -   例
            -   225mini2006d\_期近.xls
                ↓
            -   2006.xls
-   xls ファイルを開いて 1 分足シートを開きます
-   (任意)1 分足シートの右上にあるボタン「夕場同日」あるいは「ナイトセッション同」を押します
    -   これを押す事で夕場(ナイトセッション同)の日付が日中の日付と同じになります。
-   xls ファイルを xlsx ファイルに変えてください。
    -   利用パッケージ openpyxl のバージョンでは xls ファイルは非対応だからです。
    -   xlsx ファイルに変える時に xls のモジュールで定義しているマクロが消えるという警告ダイアログが表示します。
        もう利用しないので OK を押して実行してください。
-   (任意)xlsx ファイルの 1min 以外のシートは全て削除してください
    -   xlsx ファイルのロード時間短取得のために実行するのをおすすめします。

## 利用方法
用意したコマンドを実行する

### make_all_1min_history
#### 225miniでダウンロードしたエクセルファイルを納めてディレクトリを指定して1分足の過去データをcsvファイルで出力するコマンド
#### コマンド実行例
1. inputディレクトリにまとめているxlsxファイルから1min.csvという1分足の過去データファイルをoutputディレクトリに出力
    - python labo225.py make_all_1min_history --fname=1min.csv --i_dir=./input --o_dir=./output

### make_period_history
#### コマンド「make_all_1min_history」で生成した過去データファイルから他の時間足の過去データファイルを出力するコマンド
#### コマンド実行例
1. 1min.csvから1時間足の過去データtest_1h.csvファイルをoutputディレクトリに出力
    - python labo225.py make_period_history --i_csv_fname_1min=1min.csv --o_dir=./output --o_fname=test_1h.csv --minutes=60
