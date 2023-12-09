#!/usr/bin/env python
import sys
import PySimpleGUI as sg
import modules.ui.interface

# 利用するウィンドウクラス
from modules.ui.windows.main import MainWindow
from modules.ui.windows.base import BaseWindow
from modules.ui.windows.strategy_form import StrategyFormWindow
from modules.ui.model import Model


# TODO: GUIコントローラー
class ViewController(object):
    __model: Model = None
    __event_interface: modules.ui.interface.IUIViewEvent

    __main_win: MainWindow = None
    __child_win: list[BaseWindow] = list()

    __strategy_form_win: StrategyFormWindow = None

    def __init__(
        self,
        model: Model,
        # title: str,
        event_i: modules.ui.interface.IUIViewEvent,
        # size,
    ) -> None:
        self.__model = model
        self.__event_interface = event_i

        self.__main_win = MainWindow(title=self.__model.title, size=self.__model.size)
        sg.theme("Dark")

    def open(self, b_screen: bool = False):
        self.__main_win.open(b_screen=b_screen)

        self.__event_interface.event_open()

        while True:
            try:
                win, event, values = sg.read_all_windows(timeout=1)
                if self.__main_win.is_window(win):
                    if event is None:
                        break
                    if (
                        self.__main_win.update(event, values, self.__event_interface)
                        is False
                    ):
                        break

                # ループを逆順に回す事でループ中に要素を消している
                for child_win in reversed(self.__child_win):
                    if child_win.is_window(win):
                        if (
                            child_win.update(event, values, self.__event_interface)
                            is False
                        ):
                            child_win.close()
                            self.__child_win.remove(child_win)

                self.__event_interface.event_update()

            # エラーはすべてここにまとめる
            except Exception as ex:
                t, v, trace = sys.exc_info()
                self.__event_interface.event_error(t, v, trace)

        for child_win in self.__child_win:
            child_win.close()

        self.close()

    def close(self):
        self.__main_win.close()

    def open_strategy_form(self, broker_names: list[str]):
        form_win: StrategyFormWindow = StrategyFormWindow(
            "戦略設定", size=(300, 200), b_demo=True, broker_names=broker_names
        )
        form_win.open(b_screen=False)
        self.__child_win.append(form_win)

    # TODO: 取引有効設定
    def enable_trade(self, b_enable: bool):
        self.__main_win.enable_btn_trade(b_enable=b_enable)

    # TODO: 戦略項目を追加
    def add_item_strategy(self, id: int, b_demo: bool, name: str, lot: float):
        trade_name: str = "リアル"
        if b_demo:
            trade_name = "デモ"

        self.__model.add_strategy_item([id, name, trade_name, lot])
        self.__main_win.update_strategy_table(items=self.__model.strategy_items)

    # TODO: 取引項目を追加
    def add_transaction_item(
        self,
        # 注文番号
        ticket: int,
        # 注文時間
        date_time: str,
        # 戦略名
        strategy: str,
        # 証券会社
        broker: str,
        # 銘柄
        symbol: str,
        # 売買タイプ(売りか買い)
        cmd: str,
        # 売買時の価格
        volume: float,
        # 取引数量
        lot: float,
        # 損切価格
        stoploss: float = 0.0,
        # 決済価格
        takeprofit: float = 0.0,
    ):
        self.__model.add_transaction_item(
            [
                ticket,
                date_time,
                strategy,
                broker,
                symbol,
                cmd,
                volume,
                lot,
                stoploss,
                takeprofit,
            ]
        )
        self.__main_win.update_transaction_table(items=self.__model.transaction_items)
