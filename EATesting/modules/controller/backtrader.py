#!/usr/bin/env python
import modules.controller.interface as interface
import modules.model.market.interface as market_model_interface
import modules.model.controller.model as ctrl_model_interface
import modules.view.interface as view_interface

import backtrader as bt
import multiprocessing


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

        # バックテストの実行
        view.begin_draw()

        self.result_strategy = self.__cerebro.run(maxcpus=self.cpu_count)
        self.__cerebro.plot(plotter=view)

        view.end_draw()
