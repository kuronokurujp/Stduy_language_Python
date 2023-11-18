#!/usr/bin/env python
import PySimpleGUI as sg
from modules.ui.windows.base import BaseWindow
from modules.ui.interface import IUIViewEvent


# メインウィンドウクラス
class MainWindow(BaseWindow):
    # TODO: イベント名
    __EVT_BTN_RUN_TRADE: str = "EV_MW_RUN_TRADE"
    __EVT_BTN_ADD_STRATEGY: str = "EV_MW_ADD_STRATEGY"

    # TODO: 各オブジェクトのキー名
    __KEY_STATUS_BAR: str = "K_MW_STATUS_BAR"
    __KEY_STRATEGY_TABLE: str = "K_MW_ST_TABLE"
    __KEY_ACCOUNT_HI_TABLE: str = "K_MW_ACCOUNT_HI_TABLE"
    __KEY_TRANSACTION_TABLE: str = "K_MW_TRANSACRION_TABLE"

    def __init__(self, title: str, size) -> None:
        super().__init__(title=title, size=size)

        self.__layout = [
            self.__create_menubar(),
            self.__create_toolbar(),
            self.__create_strategy_layout(),
        ]
        self.__layout_tab = [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "取引",
                            self.__craete_transactions_layout(),
                        ),
                        sg.Tab(
                            "口座履歴",
                            self.__create_accunt_history_layout(),
                        ),
                        sg.Tab(
                            "サーバー",
                            self.__create_server_info_layout(),
                        ),
                        sg.Tab(
                            "操作履歴",
                            self.__create_outputlog_layout(),
                        ),
                    ]
                ],
                tab_location="bottomleft",
                expand_x=True,
            ),
        ]
        self.__status_bar = [self.__create_statusbar()]

    def open(self, b_screen: bool) -> bool:
        super().open(
            b_screen=b_screen,
            layout=[self.__layout, [sg.VPush()], self.__layout_tab, self.__status_bar],
        )

    def update(self, event_interface: IUIViewEvent) -> bool:
        event, value = self._window.read(timeout=1)
        match event:
            case (sg.WIN_CLOSED, "Exit"):
                return False
            # TODO: 自動売買ボタンを押した
            case self.__EVT_BTN_RUN_TRADE:
                event_interface.event_run_trade()
            # TODO: 戦略追加
            case self.__EVT_BTN_ADD_STRATEGY:
                # TODO: 名前の設定が必要
                event_interface.even_open_strategy_form()
            case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                return False

                # yn = sg.PopupYesNo("終了しますか?", font=("MeiryoUI", 10), keep_on_top=True)
                # if yn == "Yes":
                #     return False

        return True

    # TODO: 取引ボタン有効設定
    def enable_btn_trade(self, b_enable: bool):
        self._window[self.__EVT_BTN_RUN_TRADE].update(disabled=not b_enable)

    # TODO: 戦略テーブルを更新
    def update_strategy_table(self, datas: list):
        self._window[self.__KEY_STRATEGY_TABLE].update(values=datas)

    def __create_menubar(self) -> sg.Menu:
        return sg.Menu(
            [
                ["ファイル", ["終了"]],
                ["表示", []],
                ["ヘルプ", []],
            ]
        )

    def __create_toolbar(self) -> list:
        return [
            [
                sg.Button("自動売買", key=self.__EVT_BTN_RUN_TRADE),
                sg.Button("戦略追加", key=self.__EVT_BTN_ADD_STRATEGY),
            ]
        ]

    # TODO: アプリの操作情報
    def __create_outputlog_layout(self):
        return [[sg.Output(size=(0, 50), expand_x=True, echo_stdout_stderr=True)]]

    # TODO: サーバー情報
    def __create_server_info_layout(self):
        return [[sg.Multiline(size=(0, 50), expand_x=True, write_only=True)]]

    # TODO: 口座履歴
    def __create_accunt_history_layout(self):
        # TODO: 列名とデータキー名のマッピング作る
        headers: list = [
            "注文番号",
            "注文時間",
            "証券会社",
            "取引種別",
            "数量",
            "銘柄",
            "注文価格",
            "決済時間",
            "決済価格",
        ]
        headings = [str(headers[x]) + " .." for x in range(len(headers))]

        return (
            [
                sg.Table(
                    values=[],
                    headings=headings,
                    max_col_width=25,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification="center",
                    num_rows=20,
                    alternating_row_color="lightblue",
                    key=self.__KEY_ACCOUNT_HI_TABLE,
                    selected_row_colors="red on yellow",
                    enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    enable_click_events=True,  # Comment out to not enable header and other clicks
                    tooltip="",
                )
            ],
        )

    def __create_statusbar(self) -> list:
        return [sg.StatusBar(text="", key=self.__KEY_STATUS_BAR)]

    # TODO: 戦略レイアウト
    def __create_strategy_layout(self):
        # 列名が同じだと横のレイアウトサイズが壊れた
        headers: list = ["ID", "戦略", "WebhookURL"]
        visible_columns = [False, True, True]
        headings = [str(headers[x]) + " .." for x in range(len(headers))]

        return (
            [
                sg.Table(
                    values=[],
                    headings=headings,
                    max_col_width=25,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification="center",
                    num_rows=20,
                    alternating_row_color="lightblue",
                    key=self.__KEY_STRATEGY_TABLE,
                    selected_row_colors="red on yellow",
                    enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    enable_click_events=True,  # Comment out to not enable header and other clicks
                    tooltip="",
                    visible_column_map=visible_columns,
                )
            ],
        )

    # TODO: 取引画面
    def __craete_transactions_layout(self):
        # 列名が同じだと横のレイアウトサイズが壊れた
        # TODO: 列名とデータキー名のマッピング作る
        headers: list = ["注文番号", "時間", "証券会社", "取引種別", "数量", "銘柄", "価格"]
        headings = [str(headers[x]) + " .." for x in range(len(headers))]

        return (
            [
                sg.Table(
                    values=[],
                    headings=headings,
                    max_col_width=25,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification="center",
                    num_rows=20,
                    alternating_row_color="lightblue",
                    key=self.__KEY_TRANSACTION_TABLE,
                    selected_row_colors="red on yellow",
                    enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    enable_click_events=True,  # Comment out to not enable header and other clicks
                    tooltip="",
                )
            ],
        )
