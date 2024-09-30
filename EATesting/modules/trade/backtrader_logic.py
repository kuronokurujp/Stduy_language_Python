#!/usr/bin/env python
import modules.logics.logic_interface as logic_interface
import modules.trade.engine_interface as trade_intarface
import modules.trade.backtrader_analyzer as backtrader_analyzer
import modules.trade.analyzer_interface as analyzer_interface

import backtrader as bt
import pathlib
import configparser


# ロジックの基本クラス
class LogicBase(logic_interface.ILogic):
    # ConfigParserオブジェクトを作成
    config = configparser.ConfigParser()

    def __init__(self, logic_filepath: pathlib.Path) -> None:
        # INIファイルを読み込む
        # UTF-8エンコーディングでファイルを読み込む
        with open(logic_filepath, "r", encoding="utf-8") as configfile:
            self.config.read_file(configfile)

    def attach_test_strategy(self, trade_engine: trade_intarface.IEngine) -> None:
        # 戦略追加
        self._addstrategy(trade_engine.cerebro)

    def attach_opt_strategy(self, trade_engine: trade_intarface.IEngine) -> int:
        return self._optstrategy(trade_engine.cerebro)

    def analyzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return backtrader_analyzer.BaseAnalyzer()

    def _addstrategy(self, cerebro: bt.cerebro):
        raise NotImplementedError()

    def _optstrategy(self, cerebro: bt.cerebro) -> int:
        raise NotImplementedError()

    def show_test(self, results):
        pass

    def show_total_combination(self, total: int):
        print(f"検証回数({total})")

    def show_opt(self, results, result_put_flag: bool = False):
        # 最適化結果の取得
        if result_put_flag:
            print("==================================================")
            # 最適化結果の収集
            for stratrun in results:
                print("**************************************************")
                for strat in stratrun:
                    print("--------------------------------------------------")
                    print(strat.p._getkwargs())
                    # 残り残金
                    print(strat.p.value)
                    # トレード回数
                    print(strat.p.trades)
            print("==================================================")

        # トレードをしていないパラメータは除外する
        best_results = [result for result in results if result[0].p.trades > 0]
        if len(best_results) <= 0:
            print("トレードを一度もしていない結果しかなかった")

        # 一番高い結果から降順にソート
        best_results = sorted(best_results, key=lambda x: x[0].p.value, reverse=True)

        # 1から20位までのリストを作る
        top_20_results = best_results[:20]

        # リストの各要素の値を出力
        for result in top_20_results:
            print("資金: ", result[0].p.value)
            print("トレード回数: ", result[0].p.trades)
            print("パラメータ: ", result[0].p._getkwargs())
