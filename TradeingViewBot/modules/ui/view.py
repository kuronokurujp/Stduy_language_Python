#!/usr/bin/env python
import wx
from modules.ui.ui_appbase_frame import ui_appbase_frame

# TODO: ツールの描画
class View(ui_appbase_frame):
    __app: wx.App = None

    def __init__(self, title: str, size) -> None:
        self.__app = wx.App(False)

        super().__init__(None)
        self.SetTitle(title=title)
        self.SetSize(size)

    def open(self):
        self.Show(True)
        self.__app.MainLoop()

    def close(self):
        self.Close()
        self.__app.ExitMainLoop()
