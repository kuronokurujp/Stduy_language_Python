#!/usr/bin/env python
import PySimpleGUI as sg
from modules.ui.interface import IUIViewEvent


# ベースとなるウィンドウクラス
class BaseWindow(object):
    _window: sg.Window = None

    __title: str = ""
    __size = (0, 0)

    def __init__(self, title: str, size) -> None:
        super().__init__()

        self.__title = title
        self.__size = size

    def open(self, layout, b_screen: bool, b_model: bool = False) -> bool:
        self._window = sg.Window(
            title=self.__title,
            layout=layout,
            size=self.__size,
            keep_on_top=False,
            resizable=True,
            enable_close_attempted_event=True,
            finalize=True,
            modal=b_model
        )

        if b_screen:
            self._window.maximize()

        return True

    def close(self) -> bool:
        self._window.close()
        return True

    def update(self, event, values, event_interface: IUIViewEvent) -> bool:
        return True

    def is_window(self, window) -> bool:
        return self._window == window
