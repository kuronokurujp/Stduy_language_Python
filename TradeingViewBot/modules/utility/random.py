#!/usr/bin/env python
import uuid


# ユニークなランダム値を取得
def random_num() -> int:
    guid = uuid.uuid1()
    return int.from_bytes(guid.bytes, byteorder="big", signed=True) >> 64


# GUIDを取得
def guid() -> str:
    return str(uuid.uuid1())
