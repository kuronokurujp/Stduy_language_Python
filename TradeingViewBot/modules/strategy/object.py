#!/usr/bin/env python
import uuid


# TODO: ストラテジーのデータオブジェクト
# データ保存対象
class DataObject(object):
    # 64bitの値が入る
    # 32bitにはならない？
    __name: str = ""
    __url: str = ""
    __b_demo: bool = True

    def __init__(self, name: str, b_demo: bool, url: str) -> None:
        self.__name = name
        self.__url = url
        self.__b_demo = b_demo

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__url

    @property
    def demo(self) -> bool:
        return self.__b_demo


# TODO: ストラテジーのデータオブジェクト管理
class DataObjectManager(object):
    __objects: dict[int, DataObject] = dict()

    # TODO: オブジェクトリスト
    @property
    def objects(self) -> dict[int, DataObject]:
        return self.__objects

    def __init__(self) -> None:
        pass

    # TODO: オブジェクトの追加
    def add_object(self, name: str, url: str, b_demo: bool) -> tuple[bool, str, int]:
        # TODO: 検証処理の追加が必要

        # ユニークなIDを作る
        guid = uuid.uuid1()
        id: int = int.from_bytes(guid.bytes, byteorder="big", signed=True) >> 64
        # URLの後ろにユニークなIDをつけて一意なURLを作成
        object: DataObject = DataObject(
            name=name, url="{}/{}".format(url, guid), b_demo=b_demo
        )

        self.__objects[id] = object

        return (
            True,
            "success: add strategy id({}) / name({}) / url({})".format(
                id, object.name, object.url
            ),
            id,
        )

    # TODO: オブジェクトの破棄
    def del_object(self, id: int) -> tuple[bool, str]:
        if id in self.__objects:
            self.__objects.pop(id)
            return (True, "success: del strategy id({})".format(id))

        return (False, "error: del strategy id({})".format(id))
