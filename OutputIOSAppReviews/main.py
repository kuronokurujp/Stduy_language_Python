#!/usr/bin/env python
import argparse
import json
import requests
import pandas as pd

# appfiguresのAPIのURL
BASE_URI = "https://api.appfigures.com/v2/"


# コマンドライン引数を設定
def get_args():
    parser = argparse.ArgumentParser(
        description="iOSStoreの配信アプリのレビューを自動生成するプログラム"
    )
    parser.add_argument("app_id", type=str, help="配信しているアプリのID", default="")
    parser.add_argument("lang", type=str, help="言語", default="ja")
    parser.add_argument("country", type=str, help="言語", default="jp")
    return parser.parse_args()


# 拡張子なしのconfigファイルを読み込む関数
def load_config(config_path=".config"):
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config.get("access_token"), config.get("username")


def make_request(uri, token, **querystring_params):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(
        BASE_URI + uri.lstrip("/"), params=querystring_params, headers=headers
    )


def main(
    app_id: str,
    lang: str = "ja",
    country: str = "jp",
    config_path: str = ".config",
    output_filename: str = "ios_play_reviews.csv",
    max_page_count: int = 10,
):
    # APIキーを読み込み
    # アクセストークンとユーザー名を取得
    access_token, username = load_config(config_path)

    # Get the root resource to show we are in business
    root_response = make_request("/", token=access_token)
    assert 200 == root_response.status_code

    root_response_json = root_response.json()
    assert username == root_response_json["user"]["email"]

    # app_idからプロダクトIDを取得
    # 取得するにはあらかじめappfiguresのAppsリストに登録が必要かもしれない
    product_response = make_request(f"/products/apple/{app_id}", token=access_token)
    if 200 != product_response.status_code:
        print(product_response.text)
        return

    # appfiguresで管理している製品IDを取得
    product_id = product_response.json()["id"]

    review_data = []
    count: int = 0
    page: int = 1
    try:
        while count < max_page_count or max_page_count == -1:

            # Get a list of product reviews
            # 検索実行
            query_params = {
                "products": product_id,
                "countries": country,
                "count": 500,
                "lang": lang,
                "page": page,
            }

            reviews_response = make_request(
                "/reviews", token=access_token, **query_params
            )
            if 200 != reviews_response.status_code:
                print(reviews_response.text)
                break

            reviews = reviews_response.json()
            # レビューの抽出
            # データを整形
            for review in reviews.get("reviews"):
                review_data.append(
                    {
                        "User Name": review.get("author"),
                        "Rating": review.get("stars"),
                        "Review Text": review.get("review"),
                        "Date": review.get("date"),
                    }
                )

            count = count + 1
            page = page + 1
            page_max: int = reviews.get("pages")
            if page_max <= page:
                break
    except Exception as identifier:
        print(identifier)

    # データフレームに変換
    df = pd.DataFrame(review_data)

    # CSVファイルに出力
    df.to_csv(output_filename, index=False, encoding="utf-8-sig")

    print(f"レビューが {output_filename} に出力されました。")


if __name__ == "__main__":
    try:
        args = get_args()
        main(app_id=args.app_id, lang=args.lang, country=args.country)
    except Exception as identifier:
        print(identifier)
