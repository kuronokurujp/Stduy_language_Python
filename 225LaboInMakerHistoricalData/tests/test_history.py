import main
import os


def test_open_xls():
    print(os.getcwd())
    cmd: main.Command = main.Command()
    wb, target_sheet_names = cmd._open_xls("input/2006.xlsx")
    assert len(target_sheet_names) == 1

    wb, target_sheet_names = cmd._open_xls("input/2007.xlsx")
    assert len(target_sheet_names) == 2

    wb, target_sheet_names = cmd._open_xls("input/2008.xlsx")
    assert len(target_sheet_names) == 2

    wb, target_sheet_names = cmd._open_xls("input/2009.xlsx")
    assert len(target_sheet_names) == 2

    wb, target_sheet_names = cmd._open_xls("input/2010.xlsx")
    assert len(target_sheet_names) == 3

    wb, target_sheet_names = cmd._open_xls("input/2011.xlsx")
    assert len(target_sheet_names) == 4


def test_create_csv_file():
    cmd: main.Command = main.Command()
    # 1シートであれば成功
    wb, target_sheet_names = cmd._open_xls("input/2006.xlsx")
    # うまくいっている
    # wb, target_sheet_names = cmd._open_xls("input/2011_test.xlsx")

    test_csv_file_path = "output/test_main.csv"
    if os.path.isfile(test_csv_file_path):
        os.remove(test_csv_file_path)

    cmd._create_csv_file("output/test_main.csv")
    cmd._add_csv_data(wb, target_sheet_names)


def test_mege_csv_file():
    cmd: main.Command = main.Command()
    test_csv_file_path = "test_main_all.csv"
    if os.path.isfile(test_csv_file_path):
        os.remove(test_csv_file_path)

    cmd._create_csv_file(test_csv_file_path)

    # wb, target_sheet_names = cmd._open_xls("input/2006.xlsx")
    # cmd._add_csv_data(wb, target_sheet_names)

    wb, target_sheet_names = cmd._open_xls("input/2007.xlsx")
    cmd._add_csv_data(wb, target_sheet_names)

    # wb, target_sheet_names = cmd._open_xls("input/2008.xlsx")
    # cmd._add_csv_data(wb, target_sheet_names)


# xlsxファイルパス取得
def test_input_files():
    cmd: main.Command = main.Command()
    files: list = cmd._get_data_files(input_dtr="input/")

    assert 0 < len(files)


def test_period_history():
    cmd: main.Command = main.Command()

    output_dir: str = "output"
    # output_file_name: str = "test_main_1h.csv"
    output_file_name: str = "test_main_m15.csv"
    test_csv_file_path = os.path.join(output_dir, output_file_name)
    if os.path.isfile(test_csv_file_path):
        os.remove(test_csv_file_path)

    input_file_name: str = "test_main.csv"

    cmd.make_peroid_history_03(
        i_csv_fname_1min=os.path.join(output_dir, input_file_name),
        o_dir=output_dir,
        o_fname=output_file_name,
        minutes=15,
    )
