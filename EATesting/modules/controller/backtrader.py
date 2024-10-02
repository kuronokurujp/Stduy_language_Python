#!/usr/bin/env python
import modules.controller.interface as interface
import modules.model.market.interface as market_model_interface
import modules.model.controller.model as ctrl_model_interface
import modules.view.interface as view_interface

import backtrader as bt
import multiprocessing
from tqdm import tqdm


# バックトレードを制御するコントローラー
class Controller(interface.IController):
    cerebro: bt.Cerebro = None
    leverage: float = 1.0
    b_opt: bool = False
    result_strategy = None
    cpu_count: int = 0
    pbar = None
    __cerebro: bt.Cerebro

    def __init__(
        self,
        cerebro: bt.Cerebro,
        leverage: float = 1.0,
        b_opt: bool = False,
        cpu_count: int = 0,
    ) -> None:
        super().__init__()

        self.leverage = leverage
        self.b_opt = b_opt
        self.cpu_count = cpu_count
        # Cerebroは外部から設定される
        self.__cerebro = cerebro

    def run(
        self,
        controller_model: ctrl_model_interface.IModel,
        market_model: market_model_interface.IModel,
        view: view_interface.IView,
    ) -> None:
        # データをCerebroに追加
        self.__cerebro.adddata(market_model.prices_format_backtrader())

        # 初期資金を設定
        self.__cerebro.broker.set_cash(1000000)
        # レバレッジを変える
        # commisionは手数料
        self.__cerebro.broker.setcommission(commission=0)

        # ポジジョンサイズを変える事でレバレッジを変える
        self.__cerebro.addsizer(bt.sizers.FixedSize, stake=self.leverage)

        if self.b_opt is False:
            self.__test(model=controller_model, view=view)
        else:
            self.__opt(model=controller_model, view=view)

    def __test(
        self,
        model: ctrl_model_interface.IModel,
        view: view_interface.IView,
    ):
        # 利用する戦略をエンジンにアタッチ
        model.output_strategy()

        # カスタム解析クラス登録
        self.__cerebro.addanalyzer(model.analayzer_class(), _name="custom_analyzer")

        # バックテストの実行
        self.__cerebro.run()
        # 独自ビューをプロッターとして設定
        # ビュー内でテスト結果の描画処理をする
        self.__cerebro.plot(plotter=view)

    def __opt(
        self,
        model: ctrl_model_interface.IModel,
        view: view_interface.IView,
    ):
        total: int = model.output_strategy()
        view.log(msg=f"検証回数({total}")

        # CPUを利用数を計算
        cpu_max: int = multiprocessing.cpu_count()
        # CPUコア数最小・最大をチェック
        if self.cpu_count <= 0:
            self.cpu_count = 1
        elif cpu_max < self.cpu_count:
            self.cpu_count = cpu_max

        view.log(
            msg=f"使用するCPUコア数は({self.cpu_count}) / CPUコア最大数は({cpu_max})"
        )

        self.pbar = tqdm(smoothing=0.05, desc="最適化進捗率", total=total)

        # バックテストの実行
        self.__cerebro.optcallback(self.__optimizer_callbacks)
        self.result_strategy = self.__cerebro.run()

        if self.pbar is not None:
            self.pbar.close()

    def __show_opt(self, results, result_put_flag: bool = False):
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

    # 最適化の１処理が終わったに呼ばれるコールバック
    def __optimizer_callbacks(self, cb):
        self.pbar.update()
