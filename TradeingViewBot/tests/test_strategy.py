#!/usr/bin/env python
import modules.strategy.object
import modules.broker.const


def test_add_strategy():
    data_manager: modules.strategy.object.DataObjectManager = (
        modules.strategy.object.DataObjectManager()
    )

    for i in range(100):
        b_flg, msg, id = data_manager.add_object(
            name="test", broker_type=modules.broker.const.BROKER_TYPE_DEMO
        )
        print(msg)
        assert b_flg


def test_del_strategy():
    data_manager: modules.strategy.object.DataObjectManager = (
        modules.strategy.object.DataObjectManager()
    )

    for i in range(100):
        b_flg, msg, id = data_manager.add_object(
            name="test", broker_type=modules.broker.const.BROKER_TYPE_DEMO
        )
        print(msg)
        assert b_flg

    objs = data_manager.objects.copy()
    for id, object in objs.items():
        b_flg, msg = data_manager.del_object(id=id)
        print(msg)
        assert b_flg
