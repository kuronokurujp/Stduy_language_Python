#!/usr/bin/env python
import modules.utility.random as utility_rnd


# TODO: ストラテジーのデータオブジェクト
# データ保存対象
class DataObject(object):
    __name: str = ""
    __url: str = ""
    # TODO: 証券会社のタイプ値
    __broker_type: int = -1
    # TODO: 扱う銘柄
    __symbol_type: int = -1
    # TODO: 売買数量
    __lot: float = 1.0

    __id: int = -1

    # TODO: 注文した取引チケット一覧
    __transaction_tickets: list[int] = list[int]()

    def __init__(
        self,
        name: str,
        broker_type: int,
        symbole_type: int,
        url: str,
        id: int,
        lot: float,
    ) -> None:
        self.__name = name
        self.__url = url
        self.__broker_type = broker_type
        self.__symbol_type = symbole_type
        self.__id = id
        self.__lot = lot

    @property
    def id(self) -> int:
        return self.__id

    @property
    def symbole_type(self) -> int:
        return self.__symbol_type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__url

    @property
    def broker_type(self) -> int:
        return self.__broker_type

    @property
    def lot(self) -> float:
        return self.__lot

    @property
    def transaction_tickets(self) -> list[int]:
        return self.__transaction_tickets

    # TODO: 取引チケットを追加
    def add_ticket(self, ticket: int):
        self.__transaction_tickets.append(ticket)

    # TODO: 取引チケットを削除
    def remove_ticket(self, ticket: int):
        self.__transaction_tickets.remove(ticket)


# TODO: ストラテジーのデータオブジェクト管理
class DataObjectManager(object):
    __objects: list[DataObject] = list[DataObject]()

    # TODO: オブジェクトリスト
    @property
    def objects(self) -> list[DataObject]:
        return self.__objects

    def __init__(self) -> None:
        super().__init__()

    # TODO: オブジェクトの追加
    def add_object(
        self, name: str, broker_type: int, symbol_type: int, lot: float
    ) -> tuple[bool, str, int, int]:
        # TODO: 検証処理の追加が必要

        id: int = utility_rnd.random_num()
        # ユニークなIDを作る
        guid = utility_rnd.guid()
        # URLは固定ではなく変化するのでURLの後ろにつける値を保存
        object: DataObject = DataObject(
            name=name,
            url="{}".format(guid),
            broker_type=broker_type,
            symbole_type=symbol_type,
            id=id,
            lot=lot,
        )

        self.__objects.append(object)

        return (
            True,
            "success: add strategy id({}) / name({}) / url({})".format(
                id, object.name, object.url
            ),
            id,
            len(self.__objects) - 1,
        )

    # TODO: DataObjectのidからオブジェクトを破棄
    def del_object(self, id: int) -> tuple[bool, str]:
        hit_objs: list[DataObject] = filter(lambda obj: obj.id == id, self.__objects)
        if hit_objs is None and len(hit_objs) <= 0:
            return

        for del_obj in hit_objs:
            self.__objects.remove(del_obj)
            return (True, "success: del strategy id({})".format(del_obj.id))

        return (False, "error: del strategy id({})".format(id))

    def del_object_at(self, idx: int) -> tuple[bool, str]:
        if len(self.__objects) <= 0:
            return None

        if len(self.__objects) <= idx:
            return (False, "error: del strategy idx({})".format(idx))

        del self.__objects[idx]
        return (True, "success: del strategy idx({})".format(idx))

    # TODO: 戦略オブジェクトを取得
    def get_object(self, id: int) -> DataObject:
        hit_objs: list[DataObject] = list[DataObject](
            filter(lambda obj: obj.id == id, self.__objects)
        )
        if hit_objs is None:
            return None
        if len(hit_objs) <= 0:
            return None

        return hit_objs[0]

    # TODO: 戦略オブジェクトを取得(インデックス版)
    def get_object_at(self, idx: int) -> DataObject:
        if len(self.__objects) <= 0:
            return None

        if len(self.__objects) <= idx:
            return None
        return self.__objects[idx]
