#!/usr/bin/env python
import traceback
import modules.strategy.object as st_obj
import modules.broker.const as bk_const


def test_add_strategy():
    data_manager: st_obj.DataObjectManager = st_obj.DataObjectManager()

    for i in range(100):
        b_flg, msg, id, idx = data_manager.add_object(
            name="test",
            broker_type=bk_const.BROKER_TYPE_DEMO,
            symbol_type=0,
            lot=1,
        )

        print(msg)
        assert b_flg
        assert 0 < id
        assert 0 <= idx

    # idが重複していないかチェック
    for i in range(len(data_manager.objects) - 1):
        id = data_manager.objects[i].id
        objs = data_manager.objects[i+1:].copy()
        hit_objs: list[st_obj.DataObject] = list(
            filter(lambda obj: obj.id == id, objs)
        )
        if 0 < len(hit_objs):
            print("error: 戦略追加失敗. idが重複している({})".format(id))
            assert False



def test_del_strategy():
    data_manager: st_obj.DataObjectManager = st_obj.DataObjectManager()

    # 追加データのidで削除できるか
    for i in range(100):
        b_flg, msg, id = data_manager.add_object(
            name="test",
            broker_type=bk_const.BROKER_TYPE_DEMO,
            symbol_type=0,
            lot=1,
        )
        print("Id({}) / msg({})".format(id, msg))
        assert b_flg

    objs = data_manager.objects.copy()
    for obj in objs:
        b_flg, msg = data_manager.del_object(id=obj.id)
        print(msg)
        assert b_flg

    assert len(data_manager.objects) <= 0

    # indexでの削除ができるか
    b_flg, msg, id = data_manager.add_object(
        name="test",
        broker_type=bk_const.BROKER_TYPE_DEMO,
        symbol_type=0,
        lot=1,
    )
    print("Id({}) / msg({})".format(id, msg))
    assert b_flg

    b_flg, msg, id = data_manager.add_object(
        name="test",
        broker_type=bk_const.BROKER_TYPE_DEMO,
        symbol_type=0,
        lot=1,
    )
    b_flg, msg = data_manager.del_object_at(idx=0)
    print(msg)
    assert b_flg


def test_get_strategy():
    data_manager: st_obj.DataObjectManager = st_obj.DataObjectManager()

    b_flg, msg, id = data_manager.add_object(
        name="test",
        broker_type=bk_const.BROKER_TYPE_DEMO,
        symbol_type=0,
        lot=1,
    )
    print("Id({}) / msg({})".format(id, msg))
    assert b_flg

    try:
        # 追加データのidで削除できるか
        object: st_obj.DataObject = data_manager.get_object(id=id)
        if object is None:
            print("None object id({})".format(id))
            assert False

        # 追加したデータのidxで削除できるか
        object: st_obj.DataObject = data_manager.get_object_at(idx=0)
        if object is None:
            print("None object idx({})".format(0))
            assert False
    except Exception as ex:
        traceback.print_exc()
        assert False
