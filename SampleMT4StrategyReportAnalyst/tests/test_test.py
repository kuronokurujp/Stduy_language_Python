import mt4


def test_open_html():
    soup = mt4.load_mt4_html(
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
    )
    assert not soup is None
    print(soup)


def test_currency_name():
    name = mt4.create_currency_name(
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
    )
    assert not name is "AUDJPY"


def test_model_list():
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
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
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY_Rpoert_D1.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list: list = mt4.create_model_list(currenty_name=currenty_name, soup=soup)
    assert not model_list is None
    assert 0 < len(model_list)

    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDUSD_Rpoert_D1.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list.extend(mt4.create_model_list(currenty_name=currenty_name, soup=soup))
    assert 0 < len(model_list)

    group_model_dict: dict = mt4.create_group_model_dict(model_list=model_list)
    assert not group_model_dict is None
    assert 0 < len(group_model_dict)

    print()
    for key, value in group_model_dict.items():
        print("{}:{}".format(key, value))


def test_model_group_avg():
    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list: list = mt4.create_model_list(currenty_name=currenty_name, soup=soup)
    assert not model_list is None
    assert 0 < len(model_list)

    path: str = "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDUSD.htm"
    soup = mt4.load_mt4_html(path)
    assert not soup is None

    currenty_name: str = mt4.create_currency_name(path)
    model_list.extend(mt4.create_model_list(currenty_name=currenty_name, soup=soup))
    assert 0 < len(model_list)

    group_model_dict: dict = mt4.create_group_model_dict(model_list=model_list)
    assert not group_model_dict is None
    assert 0 < len(group_model_dict)

    print()
    for key, value in group_model_dict.items():
        model: mt4.GroupDataModel = mt4.get_avg_data_model(value)
        print("{}:{}".format(key, model.get_avg_val(type_name="prfoit_lost")))
        print("{}:{}".format(key, model.get_avg_val(type_name="drawdown_d")))
        print("{}:{}".format(key, model.get_avg_val(type_name="drawdown_p")))

def test_output_xlsx():
    avg_model_list: list = mt4.create_param_fit_model_list([
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDJPY.htm",
        "D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1\AUDUSD.htm"
    ])

    # 出力
    mt4.output_xlsx(dir_fullpath="D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\output", filename="D1", model_list=avg_model_list)

def test_class():
    class Test(object):
        value_01: int = 0

        def __init__(self) -> None:
            self.value: int = 0

    test: Test = Test()
    print(test.__dict__)

def test_file_filter():
    list: list = mt4.get_target_file_list("D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1")
    assert 0 < len(list)

    print(list)

def test_output_final_data():

    path_data_list: list = [

        # ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\D1", "D1"],
        # ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\H4", "H4"],
        # ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\H1", "H1"],
        # ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data\H1", "H1"],
        # ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230915/M15", "M15"],
        ["D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\data/20230917", "M30"],
    ]

    for path_data in path_data_list:
        list: list = mt4.get_target_file_list(path_data[0])
        assert 0 < len(list)
        avg_model_list: list = mt4.create_param_fit_model_list(list)

        # 出力
        mt4.output_xlsx(dir_fullpath="D:\Work\Study\Stduy_language_Python\SampleMT4StrategyReportAnalyst\output", filename=path_data[1], model_list=avg_model_list)

