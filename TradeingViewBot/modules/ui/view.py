#!/usr/bin/env python
import PySimpleGUI as sg
import modules.ui.interface


# TODO: ツールの描画
class View(object):
    __window: sg.Window = None
    __title: str = ""
    __event_interface: modules.ui.interface.IUIViewEvent

    __size = (0, 0)

    # TODO: イベント名
    _EVT_BTN_RUN_TRADE: str = "EV_RUN_TRADE"

    def __init__(
        self, title: str, event_i: modules.ui.interface.IUIViewEvent, size
    ) -> None:
        self.__event_interface = event_i
        self.__layout = [
            self.__create_menubar(),
            self.__create_toolbar(),
            self.__craete_transactions_layout(),
        ]
        self.__layout_tab = [
            sg.TabGroup(
                [
                    [
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

        self.__title = title
        self.__size = size

        sg.theme("Dark")

    def open(self, b_screen: bool = False):
        self.__window = sg.Window(
            title=self.__title,
            layout=[self.__layout, [sg.VPush()], self.__layout_tab, self.__status_bar],
            size=self.__size,
            keep_on_top=False,
            resizable=True,
            enable_close_attempted_event=True,
            finalize=True,
        )
        if b_screen:
            self.__window.maximize()

        self.__event_interface.event_open()
        while True:
            event, values = self.__window.read(timeout=1)

            if event in (sg.WIN_CLOSED, "Exit"):
                break
            elif event in (sg.WINDOW_CLOSE_ATTEMPTED_EVENT):
                yn = sg.PopupYesNo("終了しますか?", font=("MeiryoUI", 10), keep_on_top=True)
                if yn == "Yes":
                    break
            # TODO: 自動売買ボタンを押した
            elif event in (self._EVT_BTN_RUN_TRADE):
                self.__event_interface.event_run_trade()

            self.__event_interface.event_update()

        self.close()

    def close(self):
        self.__window.close()

    # TODO: 取引ボタン有効設定
    def setEnableByBtnRunTrade(self, enable: bool):
        self.__window[self._EVT_BTN_RUN_TRADE].update(disabled=not enable)

    def __create_menubar(self) -> sg.Menu:
        return sg.Menu(
            [
                ["ファイル", ["終了"]],
                ["表示", []],
                ["ヘルプ", []],
            ]
        )

    def __create_toolbar(self) -> list:
        return [[sg.Button("自動売買", key=self._EVT_BTN_RUN_TRADE)]]

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
                    key="-TABLE-",
                    selected_row_colors="red on yellow",
                    enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    enable_click_events=True,  # Comment out to not enable header and other clicks
                    tooltip="This is a table",
                )
            ],
        )

    def __create_statusbar(self) -> list:
        return [sg.StatusBar(text="", key="STATUS_BAR")]

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
                    key="-TABLE-",
                    selected_row_colors="red on yellow",
                    enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    enable_click_events=True,  # Comment out to not enable header and other clicks
                    tooltip="This is a table",
                )
            ],
        )
