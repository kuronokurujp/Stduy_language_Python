#!/usr/bin/env python

import pandas as pd
import json
import os

from kuro_p_pak.log import logger
from pathlib import Path


# データからゲームパラメータに変えて出力するコンバーター
class ConverterWithGameParamater(object):
    # Excelファイルのパス
    __ord_file_path: Path = None

    # 出力ディレクトリの設定
    __output_dir: Path = None

    def __init__(self, org_file_path: Path, output_dir_path: Path):
        # Excelファイルのパス()
        self.__ord_file_path = org_file_path

        # 出力ディレクトリの設定
        self.__output_dir = output_dir_path

    # 元ファイルをコンバートしてゲームデータを出力
    def convert(self, logger: logger.ILoegger):
        os.makedirs(self.__output_dir, exist_ok=True)
        excel_data = None
        try:
            # Excelファイルの読み込み
            excel_data = pd.ExcelFile(self.__ord_file_path)
        except FileNotFoundError as e:
            logger.err(f"File not found at {self.__ord_file_path}")
            raise (e)
        except Exception as e:
            logger.err(f"reading Excel file: {e}")
            raise (e)

        # 各シートを1つのJSONファイルに変換
        for sheet_name in excel_data.sheet_names:
            try:
                # 先頭に@を付けているのは非対象シート
                if sheet_name[0] == "@":
                    continue
                # シートのデータをすべて読み込む
                df = pd.read_excel(excel_data, sheet_name=sheet_name, header=None)
            except Exception as e:
                logger.warn(f"reading sheet '{sheet_name}': {e}")
                continue

            # 初期化
            description_s = None
            version_s = None
            type_start_row = None
            data_start_row = None
            data_end_row = None

            # 必要なセルの位置を取得
            try:
                for i in range(len(df)):
                    if i == 0:
                        col_size = df.iloc[:, 0].dropna().index[-1]
                        for j in range(col_size):
                            # A列の値
                            cell_value_a = df.iloc[i, j]
                            if cell_value_a == "version_s":
                                version_s = int(df.iloc[i + 1, j])
                                break
                    else:
                        # A列の値
                        cell_value_a = df.iloc[i, 0]
                        # B列の値（end用）
                        cell_value_b = df.iloc[i, 1] if len(df.columns) > 1 else None

                        if cell_value_a == "description_s":
                            description_s = df.iloc[i, 1]
                        elif cell_value_a == "data_s":
                            data_start_row = i
                        elif cell_value_a == "type_s":
                            type_start_row = i
                        elif cell_value_b == "end":
                            data_end_row = i
                            break
            except Exception as e:
                logger.warn(f"processing sheet '{sheet_name}' for required fields: {e}")
                continue

            # エラーがあればスキップ
            if description_s is None:
                logger.warn(f"Required fields missing in sheet '{sheet_name}'")
                continue
            if version_s is None:
                logger.warn(f"Required fields missing in sheet '{sheet_name}'")
                continue
            if data_start_row is None:
                logger.warn(f"Required fields missing in sheet '{sheet_name}'")
                continue
            if data_end_row is None:
                logger.warn(f"Required fields missing in sheet '{sheet_name}'")
                continue
            if type_start_row is None:
                logger.warn(f"Required fields missing in sheet '{sheet_name}'")
                continue

            # フィールド名とデータ型の取得
            try:
                data_fields_dist = {
                    value: idx
                    for idx, value in enumerate(df.iloc[data_start_row, :])
                    if pd.notna(value)
                    # セル位置基準名なのでデータ扱いはしない
                    if not value == "data_s"
                }
                data_types_dict = {
                    idx: value
                    for idx, value in enumerate(df.iloc[type_start_row, :])
                    if pd.notna(value)
                }
            except Exception as e:
                logger.warn(
                    f"reading data fields or types in sheet '{sheet_name}': {e}"
                )
                continue

            # 型情報に基づいてキャスト関数を決定
            type_cast = {"int": int, "float": float, "str": str, "id": str}

            # JSON出力用のデータ構造
            enemy_data = {
                "version": version_s,
                "data": {},
            }

            # データ部分を読み取り
            id_col_index: int = data_fields_dist["id"]
            db_index = data_start_row + 1
            for idx in range(db_index, data_end_row):
                # フィールドデータのキーをid名にする
                name: str = df.iloc[idx, id_col_index]
                field_values = {}
                try:
                    # id名をキー名にして各フィールドの値を設定
                    for field_name, col_index in data_fields_dist.items():
                        # id名はキーとしているのでフィールド値として扱わない
                        if col_index == id_col_index:
                            continue

                        # フィールドのデータタイプ名を取得
                        type_name: str = df.iloc[type_start_row, col_index]
                        if not pd.notna(type_name):
                            continue

                        # フィールド名があるか
                        if not pd.notna(df.iloc[data_start_row, col_index]):
                            continue

                        # フィールドデータを取得
                        field_value = df.iloc[idx, col_index]
                        if not pd.notna(field_value):
                            logger.warn(
                                f"{sheet_name} row {idx + 1} col {col_index}: field value none"
                            )
                            # デフォルト値を入れる
                            field_value = type_cast[type_name]()

                        # 出力するためにフィールド名をキーとしてフィールドデータを入れる
                        # フィールドのデータタイプ名に従ってキャストをする
                        field_values[field_name] = type_cast[type_name](field_value)
                except Exception as e:
                    logger.warn(
                        f"processing data in sheet '{sheet_name}', row {idx + 1}: {e}"
                    )
                    continue

                # JSONにデータを追加
                if field_values:
                    enemy_data["data"][name] = field_values

            # JSONファイルのパスと出力
            json_path = os.path.join(self.__output_dir, f"{sheet_name}.json")
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(enemy_data, f, ensure_ascii=False, indent=4)
                logger.info(
                    f"JSON file generated for sheet '{sheet_name}' at {json_path}"
                )
            except Exception as e:
                logger.err(f"writing JSON file for sheet '{sheet_name}': {e}")
                raise (e)
