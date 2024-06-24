#!/usr/bin/env python
import argparse
import json
from serpapi import GoogleSearch
import pandas as pd


# コマンドライン引数を設定
def get_args():
    parser = argparse.ArgumentParser(
        description="GooglePlayStoreの配信アプリのレビューを自動生成するプログラム"
    )
    parser.add_argument("app_id", type=str, help="配信しているアプリのID")
    parser.add_argument("lang", type=str, help="言語")
    parser.add_argument("country", type=str, help="言語")
    return parser.parse_args()


# 拡張子なしのconfigファイルを読み込む関数
def load_api_key(config_path=".config"):
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config.get("api_key")


def main(
    app_id: str,
    lang: str = "ja",
    country: str = "jp",
    config_path: str = ".config",
    output_filename: str = "google_play_reviews.csv",
    # -1にしたら全データを検索して取得
    # しかし無料枠だと最大100回までしか検索できないので注意
    max_page_count: int = 10,
):
    # APIキーを読み込み
    api_key = load_api_key(config_path)

    # SerpApiの検索パラメータ
    params = {
        "engine": "google_play_product",
        "store": "apps",
        "product_id": app_id,
        "all_reviews": "true",
        "platform": "phone",
        "sort_by": "2",
        "num": "199",
        "api_key": api_key,
        "hl": lang,
        "gl": country,
    }

    review_data = []
    count: int = 0
    try:
        while count < max_page_count or max_page_count == -1:

            # 検索実行
            # 異なるnext_page_tokenをやると検索一回分になるので注意
            # 無料だと100検索までしかできない
            search = GoogleSearch(params)
            results = search.get_dict()

            # レビューの抽出
            reviews = results.get("reviews", [])

            # データを整形
            for review in reviews:
                review_data.append(
                    {
                        "User Name": review.get("title"),
                        "Rating": review.get("rating"),
                        "Review Text": review.get("snippet"),
                        "Date": review.get("date"),
                    }
                )

            # next_page_tokenがあればまだレビューデータがあるので取得する
            next_token = results.get("serpapi_pagination", {}).get("next_page_token")
            if not next_token:
                break

            params["next_page_token"] = next_token
            count = count + 1
    except Exception as identifier:
        print(identifier)

    # データフレームに変換
    df = pd.DataFrame(review_data)

    # CSVファイルに出力
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")

    print(f"レビューが {output_filename} に出力されました。")


if __name__ == "__main__":
    try:
        # 取得したいアプリのID（Google PlayのURLの`id`パラメータ）
        args = get_args()
        app_id = "com.example.app"  # ここにアプリIDを入力してください
        main(app_id=args.app_id, lang=args.lang, country=args.country)
    except Exception as identifier:
        print(identifier)
