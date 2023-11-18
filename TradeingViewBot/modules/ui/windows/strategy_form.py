import PySimpleGUI as sg
from modules.ui.windows.base import BaseWindow
from modules.ui.interface import IUIViewEvent


# TODO: 戦略フォームウィンドウ
# 戦略情報の入力フォームウィンドウ
class StrategyFormWindow(BaseWindow):
    __EVT_BTN_OK: str = "EV_STRATEGY_FORM_OK"
    __EVT_INPUT_NAME: str = "EV_STRATEGY_FORM_INPUT_NAME"

    def __init__(self, title: str, size) -> None:
        super().__init__(title=title, size=size)

        self.__layout = [
            [sg.Input("戦略名", enable_events=True, key=self.__EVT_INPUT_NAME)],
            sg.Button("OK", button_color=("white", "black"), key=self.__EVT_BTN_OK),
        ]

    def open(self, b_screen: bool) -> bool:
        super().open(b_screen=b_screen, layout=[self.__layout])

    def update(self, event_interface: IUIViewEvent) -> bool:
        event, value = self._window.read(timeout=1)
        match event:
            case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                return False
            case self.__EVT_BTN_OK:
                event_interface.even_add_strategy(name=value[self.__EVT_INPUT_NAME])
                # TODO: 一度目は成功するが二度目はエラーになった
                return False

        return True
