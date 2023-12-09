import PySimpleGUI as sg
from modules.ui.windows.base import BaseWindow
from modules.ui.interface import IUIViewEvent


# TODO: 戦略フォームウィンドウ
# 戦略情報の入力フォームウィンドウ
class StrategyFormWindow(BaseWindow):
    __EVT_BTN_OK: str = "EV_STRATEGY_FORM_OK"
    __EVT_BROKER_COMBO: str = "EV_STRATEGY_BROKER_COMBO"
    __EVT_INPUT_NAME: str = "EV_STRATEGY_FORM_INPUT_NAME"
    __EVT_LOT_VAL: str = "EV_STRATEGY_INPUT_LOT_VAL"

    def __init__(self, title: str, size, b_demo: bool, broker_names: list[str]) -> None:
        super().__init__(title=title, size=size)

        self.__layout = [
            [sg.I("戦略名", enable_events=True, key=self.__EVT_INPUT_NAME)],
            [
                [sg.Text("利用する証券会社")],
                [
                    sg.Combo(
                        broker_names,
                        default_value=broker_names[0],
                        size=(30, 1),
                        key=self.__EVT_BROKER_COMBO,
                        readonly=True,
                    )
                ],
            ],
            [sg.Text("取引数量")],
            [sg.I("1.0", enable_events=True, key=self.__EVT_LOT_VAL)],
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
                # TODO: 入力が問題ないかバリデーションチェックが必要
                broker_name: str = values[self.__EVT_BROKER_COMBO]
                name: str = values[self.__EVT_INPUT_NAME]
                # TODO: 数値以外の値も入る
                lot: float = values[self.__EVT_LOT_VAL]

                # TODO: symbole_typeがいったん0にしておく
                # TODO: 選択した証券会社に応じて選べるシンボルは変えるべきだ
                event_interface.event_add_strategy(
                    name=name, broker_name=broker_name, symbole_type=0, lot=lot
                )
                return False

        return True
