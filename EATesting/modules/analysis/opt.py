#!/usr/bin/env python
from pathlib import Path
import pandas as pd


class Opt(object):
    __output_dirpath__: Path
    __input_filepath__: Path

    def __init__(self, output_dirpath: Path, input_filepath: Path):
        self.__output_dirpath__ = output_dirpath
        self.__input_filepath__ = input_filepath

    def plot(self) -> str:
        # 分割してロードする
        # データ量が数千万以上になるケースがあるから
        mode: str = "w"
        b_header: bool = False
        best_result_filepath: Path = self.__output_dirpath__.joinpath(
            "最適化結果(利益のみ).csv"
        )
        for chunk in pd.read_csv(self.__input_filepath__.absolute(), chunksize=100000):
            # トレード回数があるデータを取得
            best_results: pd.DataFrame = chunk[
                (chunk["トレード回数"] > 0) & (chunk["資金増減"] > 0)
            ]

            # 解析結果を出力
            best_results.to_csv(
                best_result_filepath,
                index=False,
                header=b_header,
                mode=mode,
            )
            # 初回処理が終わった追加モードへ移行
            b_header = True
            mode = "a"

        # 結果をテキストを作る
        msg: str = (
            f"解析完了しました\n"
            f"解析ファイル({self.__input_filepath__.absolute()})\n"
            f"解析結果\n"
            f"{best_result_filepath.absolute()}"
        )

        return msg
