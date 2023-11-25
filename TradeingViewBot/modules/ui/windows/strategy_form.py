import PySimpleGUI as sg
from modules.ui.windows.base import BaseWindow
from modules.ui.interface import IUIViewEvent


# TODO: 戦略フォームウィンドウ
# 戦略情報の入力フォームウィンドウ
class StrategyFormWindow(BaseWindow):
    __EVT_BTN_OK: str = "EV_STRATEGY_FORM_OK"
    __EVT_DEMO_CHECK: str = "EV_STRATEGY_DEMO_CHECK"
    __EVT_INPUT_NAME: str = "EV_STRATEGY_FORM_INPUT_NAME"

    def __init__(self, title: str, size, b_demo: bool, broker_names: list[str]) -> None:
        super().__init__(title=title, size=size)

        self.__layout = [
            [sg.I("戦略名", enable_events=True, key=self.__EVT_INPUT_NAME)],
            [
                sg.Checkbox(
                    "デモ", default=b_demo, enable_events=True, key=self.__EVT_DEMO_CHECK
                )
            ],
            [
                # ボタンを中央寄せにするためにしている
                sg.Column(
                    [
                        [
                            sg.B(
                                "OK",
                                button_color=("white", "black"),
                                key=self.__EVT_BTN_OK,
                            )
                        ]
                    ],
                    justification="c",
                )
            ],
        ]

    def open(self, b_screen: bool) -> bool:
        # 表示する時は他のウィンドウは操作させない
        super().open(b_screen=b_screen, layout=[self.__layout], b_model=True)

    def update(self, event, values, event_interface: IUIViewEvent) -> bool:
        if event is None:
            return False

        match event:
            case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                return False
            case self.__EVT_BTN_OK:
                b_demo: bool = values[self.__EVT_DEMO_CHECK]
                name: str = values[self.__EVT_INPUT_NAME]
                event_interface.even_add_strategy(name=name, b_demo=b_demo)
                return False

        return True
