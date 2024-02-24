#!/usr/bin/env python
import PySimpleGUI as sg
from modules.ui.windows.base import BaseWindow
from modules.ui.interface import IUIViewEvent

import modules.ui.interface as ui_interface


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

    # 右クリックを押した時の戦略テーブルのプルダウンメニュー一覧
    # 項目名::キー
    # キーは画面に表示しない
    __KEY_STRATEGY_SETTING: str = "設定::STRATEGY_MENU"
    __KEY_STRATEGY_TRADE_BUY: str = "新規買::STRATEGY_MENU"
    __KEY_STRATEGY_TRADE_SELL: str = "新規売::STRATEGY_MENU"
    __KEY_STRATEGY_TRADE_ALL_CLOSE: str = "全決済::STRATEGY_MENU"

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
                            self.__create_account_history_layout(),
                        ),
                        # sg.Tab(
                        #     "サーバー",
                        #     self.__create_server_info_layout(),
                        # ),
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

        self.__st_table = self._window[self.__KEY_STRATEGY_TABLE]
        treeview = self.__st_table.widget

        # TODO: 別テーブルでも似たようなことするかも知れないので共通処理にしたほうがいいかも
        def __update_event_st_table_click(event):
            self.__st_table.user_bind_event = event
            self.__st_table._table_clicked(event)

        treeview.bind("<Button-1>", __update_event_st_table_click)
        if sg.running_mac():
            treeview.bind("<Button-2>", __update_event_st_table_click)
        else:
            treeview.bind("<Button-3>", __update_event_st_table_click)

    def update(self, event, values, event_interface: IUIViewEvent) -> bool:
        match event:
            case (sg.WIN_CLOSED, "Exit"):
                return False
            # 自動売買ボタンを押した
            case self.__EVT_BTN_RUN_TRADE:
                event_interface.event_run_trade()
            # 戦略を追加時の設定
            case self.__EVT_BTN_ADD_STRATEGY:
                event_interface.event_new_strategy()
            case sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
                return False
                # 閉じる時に確認画面は不要と判断
                # yn = sg.PopupYesNo("終了しますか?", font=("MeiryoUI", 10), keep_on_top=True)
                # if yn == "Yes":
                #     return False
            case self.__KEY_STRATEGY_SETTING:
                # TODO: 戦略設定画面を開く
                pass
            case self.__KEY_STRATEGY_TRADE_BUY:
                # TODO: 選択した戦略で手動買い注文
                st_table: sg.Table = self._window[self.__KEY_STRATEGY_TABLE]
                if 0 < len(st_table.SelectedRows):
                    # TODO: データを取得
                    st_idx: int = st_table.SelectedRows[0]
                    event_interface.event_simple_order(
                        st_idx=st_idx, cmd=ui_interface.ORDER_BUY
                    )
                else:
                    # TODO: 選択していない状態ではエラーなので表示する
                    pass
            case self.__KEY_STRATEGY_TRADE_SELL:
                # TODO: 選択した戦略で手動売り注文
                st_table: sg.Table = self._window[self.__KEY_STRATEGY_TABLE]
                if 0 < len(st_table.SelectedRows):
                    st_idx: int = st_table.SelectedRows[0]
                    event_interface.event_simple_order(
                        st_idx=st_idx, cmd=ui_interface.ORDER_SELL
                    )
                else:
                    # TODO: 選択していない状態ではエラーなので表示する
                    pass

            case self.__KEY_STRATEGY_TRADE_ALL_CLOSE:
                # TODO: 選択した戦略の全決済
                st_table: sg.Table = self._window[self.__KEY_STRATEGY_TABLE]
                if 0 < len(st_table.SelectedRows):
                    st_idx: int = st_table.SelectedRows[0]
                    event_interface.event_all_close(st_idx=st_idx)
        if (
            isinstance(event, tuple)
            and len(event) == 3
            and event[:2] == (self.__KEY_STRATEGY_TABLE, "+CLICKED+")
        ):
            # 右クリックのみ反応させる
            if event[2][0] is not None:
                mouse = self.__st_table.user_bind_event.num
                # 左クリック押したら選択解除
                if mouse == 1:
                    self.__st_table.update(self.__st_table.get())
                    # print("L click")
                else:
                    # クリックしたセル情報がeventにタプル型で入っている
                    pass

        return True

    # TODO: 取引ボタン有効設定
    def enable_btn_trade(self, b_enable: bool):
        btn = self._window.find_element(self.__EVT_BTN_RUN_TRADE)
        # self._window[self.__EVT_BTN_RUN_TRADE].update(disabled=not b_enable)
        btn.update(disabled=not b_enable)

    # TODO: 戦略テーブルを更新
    def update_strategy_table(self, items: list):
        table = self._window.find_element(self.__KEY_STRATEGY_TABLE)
        table.update(values=items)

    # TODO: 取引テーブルを更新
    def update_transaction_table(self, items: list):
        table = self._window.find_element(self.__KEY_TRANSACTION_TABLE)
        table.update(values=items)

    # TODO: 口座履歴テーブルを更新
    def update_account_history_table(self, items: list):
        table = self._window.find_element(self.__KEY_ACCOUNT_HI_TABLE)
        table.update(values=items)

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

    # TODO: 左クリック押したら選択解除
    # TODO: 口座履歴
    def __create_account_history_layout(self):
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
        # テキスト色を黒にしている
        text_color = '#000'

        return (
            [
                sg.Table(
                    values=[],
                    text_color=text_color,
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
                    # Comment out to not enable header and other clicks
                    enable_click_events=True,
                )
            ],
        )

    def __create_statusbar(self) -> list:
        return [sg.StatusBar(text="", key=self.__KEY_STATUS_BAR)]

    # TODO: 戦略レイアウト
    def __create_strategy_layout(self):
        # 列名が同じだと横のレイアウトサイズが壊れた
        # TODO: テーブルのヘッダーなど各列を要素にしてリストにまとめることはできないかな
        # 以下のやり方だと列追加でバグが起きやすい
        headers: list = ["ID", "取引", "戦略", "取引数量"]
        visible_columns: list[bool] = [False, True, True, True]
        headings = [str(headers[x]) + " .." for x in range(len(headers))]

        # テキスト色を黒にしている
        text_color = '#000'
        return (
            [
                sg.Table(
                    values=[],
                    # 1行のみ選択
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    text_color=text_color,
                    headings=headings,
                    max_col_width=25,
                    auto_size_columns=True,
                    display_row_numbers=False,
                    justification="center",
                    num_rows=20,
                    alternating_row_color="lightblue",
                    key=self.__KEY_STRATEGY_TABLE,
                    selected_row_colors="red on yellow",
                    # enable_events=True,
                    expand_x=True,
                    expand_y=False,
                    vertical_scroll_only=False,
                    visible_column_map=visible_columns,
                    # 右クリックで選択？
                    # Comment out to not enable header and other clicks
                    enable_click_events=True,
                    right_click_selects=True,
                    # 押せるかどうか制御できる？
                    right_click_menu=[
                        "",
                        [
                            self.__KEY_STRATEGY_SETTING,
                            self.__KEY_STRATEGY_TRADE_BUY,
                            self.__KEY_STRATEGY_TRADE_SELL,
                            self.__KEY_STRATEGY_TRADE_ALL_CLOSE,
                        ],
                    ],
                )
            ],
        )

    # TODO: 取引画面
    def __craete_transactions_layout(self):
        # 列名が同じだと横のレイアウトサイズが壊れた
        # TODO: 列名とデータキー名のマッピング作る
        headers: list = [
            "注文番号",
            "時間",
            "戦略",
            "証券会社",
            "銘柄",
            "取引種別",
            "価格",
            "数量",
            "損切価格",
            "決済価格",
        ]
        # テキスト色を黒にしている
        text_color = '#000'

        headings = [str(headers[x]) + " .." for x in range(len(headers))]
        visible_columns: list[bool] = [
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
        ]

        return (
            [
                sg.Table(
                    values=[],
                    headings=headings,
                    text_color=text_color,
                    visible_column_map=visible_columns,
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
                    # Comment out to not enable header and other clicks
                    enable_click_events=True,
                )
            ],
        )
