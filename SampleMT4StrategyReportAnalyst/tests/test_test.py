import mt4
from pathlib import Path
import json


def test_open_html():
    soup = mt4.load_mt4_html(
        # "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230919/H1/USDJPY.htm"
    )
    assert not soup is None
    print(soup)


def test_currency_name():
    name = mt4.create_currency_name(
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
    )
    assert name != "AUDJPY"


def test_model_list():
    # path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230919/H1/USDJPY.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list: list = mt4.create_model_list(currenty_name=currenty_name, soup=soup)
    assert not model_list is None
    assert 0 < len(model_list)

    print()
    for model in model_list:
        print(model.__dict__)


def test_model_group():
    model_dict: dict[str, list[model_list]] = dict()
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDJPY_Rpoert_D1.htm"
    # path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230919/H1/USDJPY.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list: list[mt4.DataModel] = mt4.create_model_list(
        currenty_name=currenty_name, soup=soup
    )
    assert not model_list is None
    assert 0 < len(model_list)
    model_dict[currenty_name] = model_list

    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDUSD_Rpoert_D1.htm"
    # path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230919/H1/AUDJPY.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    # model_list.extend(mt4.create_model_list(currenty_name=currenty_name, soup=soup))
    model_list: list[mt4.DataModel] = mt4.create_model_list(
        currenty_name=currenty_name, soup=soup
    )
    assert not model_list is None
    assert 0 < len(model_list)
    model_dict[currenty_name] = model_list

    group_model_dict: dict[
        str, list[mt4.DataModel]
    ] = mt4.create_param_group_model_dict(model_dict=model_dict)
    assert not group_model_dict is None
    assert 0 < len(group_model_dict)

    from pprint import pprint

    print()
    print("num({})".format(len(group_model_dict.values())))
    for key, value in group_model_dict.items():
        assert 0 <= len(value)
        assert len(value) <= 2
        pprint("{}".format(key))
        for model in value:
            pprint("currenty_name:{}".format(model.curreny_name))


def test_model_group_avg():
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDJPY.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list: list = mt4.create_model_list(currenty_name=currenty_name, soup=soup)
    assert not model_list is None
    assert 0 < len(model_list)

    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDUSD.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list.extend(mt4.create_model_list(currenty_name=currenty_name, soup=soup))
    assert 0 < len(model_list)

    group_model_dict: dict = mt4.create_param_group_model_dict(model_dict=model_list)
    assert not group_model_dict is None
    assert 0 < len(group_model_dict)

    print()
    for key, value in group_model_dict.items():
        model: mt4.ParamPairModel = mt4.get_avg_data_model(value)
        print("{}:{}".format(key, model.get_avg_val(type_name="prfoit_lost")))
        print("{}:{}".format(key, model.get_avg_val(type_name="drawdown_d")))
        print("{}:{}".format(key, model.get_avg_val(type_name="drawdown_p")))


def test_create_currency_model_dict():
    dict: dict[str, list[mt4.DataModel]] = mt4.create_currency_model_dict(
        [
            "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDJPY_Rpoert_D1.htm",
            "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDUSD_Rpoert_D1.htm",
        ]
    )
    assert "AUDJPY" in dict
    assert "AUDUSD" in dict

    from pprint import pprint

    for key, value in dict.items():
        assert not value is None
        assert 0 < len(value)
        for model in value:
            assert key == model.curreny_name

            pprint("no:{}".format(model.no))
            pprint("currency:{}".format(model.curreny_name))


def test_output_xlsx():
    dict: dict[str, list[mt4.DataModel]] = mt4.create_currency_model_dict(
        [
            "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDJPY_Rpoert_D1.htm",
            "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230902/D1\AUDUSD_Rpoert_D1.htm",
        ]
    )
    avg_model_list: list = mt4.conv_currenty_model_dict_to_param_pair_model_list(dict)

    # 出力
    mt4.output_xlsx(
        dir_fullpath="D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\output",
        filename="D1",
        pair_model_list=avg_model_list,
        curreny_model_dict=dict,
    )


def test_class():
    class Test(object):
        value_01: int = 0

        def __init__(self) -> None:
            self.value: int = 0

    test: Test = Test()
    print(test.__dict__)


def test_file_filter():
    list: list = mt4.get_target_file_list(
        dir_filenamt="D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/new/D1",
        # ignore_currenty_names=["AUDJPY"],
        ignore_currenty_names=None,
    )
    assert 0 < len(list)
    # assert 7 == len(list)
    assert 8 == len(list)
    from pprint import pprint

    pprint(list)


def test_output_final_data():
    param_name_dict = None
    param_jp_name_json_path: Path = Path("data/param_name.json")
    if not param_jp_name_json_path is None:
        if param_jp_name_json_path.exists():
            with param_jp_name_json_path.open(encoding="utf-8") as f:
                param_name_dict = json.load(f)

    path_data_list: list = [
        [
            "C:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\output/H4",
            "20231202_H4",
            None,
        ],
    ]

    for path_data in path_data_list:
        list: list = mt4.get_target_file_list(
            path_data[0], ignore_currenty_names=path_data[2]
        )
        assert 0 < len(list)

        dict: dict[str, list[mt4.DataModel]] = mt4.create_currency_model_dict(
            path_filename_list=list
        )
        pair_model_list: list = mt4.conv_currenty_model_dict_to_param_pair_model_list(
            dict
        )

        # 出力
        mt4.output_xlsx(
            dir_fullpath="C:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\output",
            filename=path_data[1],
            pair_model_list=pair_model_list,
            curreny_model_dict=dict,
            param_name_dict=param_name_dict,
        )
