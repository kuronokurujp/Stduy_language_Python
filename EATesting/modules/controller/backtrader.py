#!/usr/bin/env python
import modules.controller.interface as interface
import modules.model.market.interface as market_model_interface
import modules.model.controller.model as ctrl_model_interface
import modules.strategy.backtrader.backtrader_strategy as bk_st
import modules.view.interface as view_interface

import psutil
import backtrader as bt
import multiprocessing
import os


# バックトレードを制御するコントローラー
class Controller(interface.IController):
    cerebro: bt.Cerebro = None
    leverage: float = 1.0
    result_strategy = None
    cpu_count: int = 0
    pbar = None

    def __init__(
        self,
        leverage: float = 1.0,
        cpu_count: int = 0,
    ) -> None:
        super().__init__()

        self.leverage = leverage
        self.cpu_count = cpu_count

    def run(
        self,
        model: ctrl_model_interface.IModel,
        market_model: market_model_interface.IModel,
        view: view_interface.IView,
    ) -> None:
        # モデルが有効か
        if model.err_msg() is not None:
            raise ValueError(model.err_msg())

        if market_model.err_msg() is not None:
            raise ValueError(market_model.err_msg())

        cerebro = bt.Cerebro()

        # マネージャーを使用してログQueueを作成
        manager = multiprocessing.Manager()
        log_queue = manager.Queue()
        cerebro.log_queue = log_queue

        # データをCerebroに追加
        cerebro.adddata(market_model.prices_format_backtrader())

        # 初期資金を設定
        cerebro.broker.set_cash(model.get_cash())
        view.log(f"初期資金: {model.get_cash()}")

        # レバレッジを変える
        # commisionは手数料
        commission: int = 0
        cerebro.broker.setcommission(commission=commission)
        view.log(f"手数料: {commission}")

        # 発注時のタイミングは次の時間軸の初め値にする
        cerebro.broker.set_coc(False)

        # ポジジョンサイズを変える事でレバレッジを変える
        # 取引数量を固定値で設定
        cerebro.addsizer(bt.sizers.FixedSize, stake=self.leverage)

        if model.is_strategy_mode():
            self.__test(cerebro=cerebro, model=model, view=view)
        else:
            self.__opt(cerebro=cerebro, model=model, view=view)

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

        while not cerebro.log_queue.empty():
            log_message = cerebro.log_queue.get()
            view.log(log_message)

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

        # プロセスに使用するコアを設定
        cpu_count: int = psutil.cpu_count()
        # CPUコアが2つ以上であればメインCPUコア以外のコアを利用する設定をする
        if 2 <= cpu_count:
            # 利用したいCPUコア数が過剰だった場合はメインCPUコア以外のをコア選択リストを生成
            select_cpu_list: list[int] = []
            if cpu_count <= self.cpu_count:
                # メインコア(0)を除く全てのコアを選択したリストを生成
                select_cpu_list = range(1, cpu_count + 1)
            else:
                # メインコア(0)を除く利用率が低いコアを選択したリストを生成
                # 各コアのCPU使用率を取得
                cpu_usage = psutil.cpu_percent(percpu=True)
                # 使用率の低い順に辞書を作成
                cpu_usage_dict = {
                    i: usage
                    for i, usage in sorted(enumerate(cpu_usage), key=lambda x: x[1])
                }

                # メインCPUは項目は削除
                del cpu_usage_dict[0]
                if 2 <= len(cpu_usage_dict):
                    select_cpu_list = list(cpu_usage_dict.keys())

            if 2 <= len(select_cpu_list):
                process = psutil.Process(os.getpid())
                process.cpu_affinity(select_cpu_list)

        # バックテストの実行
        view.begin_draw(total=total, cerebro=cerebro)

        results = cerebro.run(maxcpus=self.cpu_count)

        while not cerebro.log_queue.empty():
            log_message = cerebro.log_queue.get()
            view.log(log_message)

        view.end_draw(result=results, cash=model.get_cash())
