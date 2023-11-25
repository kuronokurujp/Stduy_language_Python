#!/usr/bin/env python
import modules.utility.random as utility_rnd


# TODO: ストラテジーのデータオブジェクト
# データ保存対象
class DataObject(object):
    # 64bitの値が入る
    # 32bitにはならない？
    __name: str = ""
    __url: str = ""
    # TODO: 証券会社のタイプ値
    __broker_type: int = -1

    def __init__(self, name: str, broker_type: int, url: str) -> None:
        self.__name = name
        self.__url = url
        self.__broker_type = broker_type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__url

    @property
    def broker_type(self) -> int:
        return self.__broker_type


# TODO: ストラテジーのデータオブジェクト管理
class DataObjectManager(object):
    __objects: dict[int, DataObject] = dict()

    # TODO: オブジェクトリスト
    @property
    def objects(self) -> dict[int, DataObject]:
        return self.__objects

    def __init__(self) -> None:
        super().__init__()

    # TODO: オブジェクトの追加
    def add_object(self, name: str, broker_type: int) -> tuple[bool, str, int]:
        # TODO: 検証処理の追加が必要

        # ユニークなIDを作る
        guid = utility_rnd.guid()
        # URLは固定ではなく変化するのでURLの後ろにつける値を保存
        object: DataObject = DataObject(
            name=name, url="{}".format(guid), broker_type=broker_type
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
