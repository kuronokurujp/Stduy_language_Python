#!/usr/bin/env python
import modules.controller.interface as interface
import modules.model.market.interface as market_model_interface
import modules.model.controller.model as ctrl_model_interface
import modules.strategy.backtrader.backtrader_strategy as bk_st
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

    def __init__(
        self,
        leverage: float = 1.0,
        b_opt: bool = False,
        cpu_count: int = 0,
    ) -> None:
        super().__init__()

        self.leverage = leverage
        self.b_opt = b_opt
        self.cpu_count = cpu_count

    def run(
        self,
        controller_model: ctrl_model_interface.IModel,
        market_model: market_model_interface.IModel,
        view: view_interface.IView,
    ) -> None:
        cerebro = bt.Cerebro()

        # データをCerebroに追加
        cerebro.adddata(market_model.prices_format_backtrader())

        # 初期資金を設定
        cerebro.broker.set_cash(controller_model.get_cash())

        # レバレッジを変える
        # commisionは手数料
        cerebro.broker.setcommission(commission=0)

        # 発注時のタイミングは次の時間軸の初め値にする
        cerebro.broker.set_coc(False)

        # ポジジョンサイズを変える事でレバレッジを変える
        # 取引数量を固定値で設定
        cerebro.addsizer(bt.sizers.FixedSize, stake=self.leverage)

        if self.b_opt is False:
            self.__test(cerebro=cerebro, model=controller_model, view=view)
        else:
            self.__opt(cerebro=cerebro, model=controller_model, view=view)

    def __test(
        self,
        cerebro: bt.Cerebro,
        model: ctrl_model_interface.IModel,
        view: view_interface.IView,
    ):
        # 利用する戦略をエンジンにアタッチ
        add_strategy_func = model.strategy_add_func()
        # 処理によって取得する関数の引数が違う
        add_strategy_func(cerebro, model.get_param("test"))

        # カスタム解析クラス登録
        cerebro.addanalyzer(model.analayzer_class(), _name="custom_analyzer")

        # バックテストの実行
        strategies = cerebro.run()

        # キャンセルした場合はplotはしない
        strategy_instance: bk_st.BaseStrategy = strategies[0]
        if strategy_instance.is_cancel:
            return

        # 独自ビューをプロッターとして設定
        # ビュー内でテスト結果の描画処理をする
        cerebro.plot(plotter=view)

    def __opt(
        self,
        cerebro: bt.Cerebro,
        model: ctrl_model_interface.IModel,
        view: view_interface.IView,
    ):
        add_strategy_func = model.strategy_add_func()
        total: int = add_strategy_func(cerebro, model.get_param("opt"))

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
        view.begin_draw(total=total, cerebro=cerebro)

        results = cerebro.run(maxcpus=self.cpu_count)

        view.end_draw(result=results, cash=model.get_cash())
