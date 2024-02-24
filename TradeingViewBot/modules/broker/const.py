#!/usr/bin/env python

# ブローカータイプ
BROKER_TYPE_NONE: int = -1
BROKER_TYPE_DEMO: int = 0
BROKER_TYPE_RAKUTEN_RSS: int = 1

# ブローカータイプ名
BROKER_TYPE_MAP: dict[int, str] = {
    BROKER_TYPE_DEMO: "デモ",
    BROKER_TYPE_RAKUTEN_RSS: "楽天証券",
}

# 証券会社が扱うシンボル
SYMBOL_TYPE_225_MINI: int = 0
SYMBOL_TYPE_MAP: dict[int, str] = {SYMBOL_TYPE_225_MINI: "日経先物Mini"}

# 注文コマンド
CMD_ORDER_BUY: int = 0
CMD_ORDER_SELL: int = 1
# 注文コマンド名
CMD_ORDER_TYPE_MAP: dict[int, str] = {CMD_ORDER_BUY: "新規買", CMD_ORDER_SELL: "新規売"}

# エラーコード
ERR_CODE_MISS_CMD_PARAM: int = 100
ERR_CODE_MAP: dict[int, str] = {ERR_CODE_MISS_CMD_PARAM: "売買タイプのパラメータに問題"}
