#!/usr/bin/env python
import PySimpleGUI as sg
import modules.ui.interface

# 利用するウィンドウクラス
from modules.ui.windows.main import MainWindow
from modules.ui.windows.base import BaseWindow
from modules.ui.windows.strategy_form import StrategyFormWindow


# TODO: GUIコントローラー
class ViewController(object):
    __event_interface: modules.ui.interface.IUIViewEvent
    __b_debug: bool = False

    __main_win: MainWindow = None
    __child_win: list[BaseWindow] = list()

    __strategy_form_win: StrategyFormWindow = None

    __strategy_datas: list = list()

    def __init__(
        self,
        title: str,
        event_i: modules.ui.interface.IUIViewEvent,
        size,
        b_debug: bool = False,
    ) -> None:
        self.__b_debug = b_debug
        self.__event_interface = event_i

        self.__main_win = MainWindow(title=title, size=size)
        sg.theme("Dark")

    def open(self, b_screen: bool = False):
        self.__main_win.open(b_screen=b_screen)

        self.__event_interface.event_open()

        while True:
            try:
                if self.__main_win.update(self.__event_interface) is False:
                    break

                # ループを逆順に回す事でループ中に要素を消している
                for child_win in reversed(self.__child_win):
                    if child_win.update(self.__event_interface) is False:
                        child_win.close()
                        self.__child_win.remove(child_win)

                self.__event_interface.event_update()

            except Exception as ex:
                self.__event_interface.event_error(ex)

        for child_win in self.__child_win:
            child_win.close()

        self.close()

    def close(self):
        self.__main_win.close()

    def open_strategy_form(self):
        form_win: StrategyFormWindow = StrategyFormWindow("追加する戦略設定", size=(300, 200))
        form_win.open(b_screen=False)
        self.__child_win.append(form_win)

    # TODO: 取引有効設定
    def enable_trade(self, b_enable: bool):
        self.__main_win.enable_btn_trade(b_enable=b_enable)

    # TODO: 戦略項目を追加
    def add_item_strategy(self, id: int, name: str, url: str):
        self.__strategy_datas.append([id, name, url])
        self.__main_win.update_strategy_table(datas=self.__strategy_datas)
