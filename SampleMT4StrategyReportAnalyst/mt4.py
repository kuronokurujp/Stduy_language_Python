from pathlib import Path
import statistics
import bs4  # ライブラリbs4をインポートする
import openpyxl


class BaseDataModel(object):
    def __init__(self) -> None:
        # パス
        self.no: float = 0.0
        # 損益
        self.prfoit_lost: float = 0.0
        # 総取引数
        self.total_number_transactions: float = 0.0
        # プロフィットファクタ
        self.profit_factor: float = 0.0
        # 期待利得
        self.expected_gain: float = 0.0
        # ドローダウン $
        self.drawdown_d: float = 0.0
        # ドローダウン %
        self.drawdown_p: float = 0.0


class DataModel(BaseDataModel):
    def __init__(self, curreny_name: str, html_list: list = None) -> None:
        super().__init__()

        if not html_list is None:
            count: int = 0
            for v in vars(self).items():
                e_soup: bs4.BeautifulStoneSoup = bs4.BeautifulSoup(
                    str(html_list[count]), "html.parser"
                )
                val_list = list(e_soup.find("td"))

                key: str = str(v[0])
                value: float = float(val_list[0])
                self.__dict__[key] = value

                count = count + 1

            # パラメータ取得
            e_soup: bs4.BeautifulStoneSoup = bs4.BeautifulSoup(
                str(html_list[0]), "html.parser"
            )
            val_list = list(e_soup.find_all("td"))
            self.params = val_list[0].attrs["title"]
        else:
            self.params = ""

        self.curreny_name = curreny_name


class GroupDataModel(object):
    def __init__(self, model_list: list) -> None:
        # パス
        self.no: float = model_list[0].no
        self.params: str = model_list[0].params
        self.model_list: list[DataModel] = model_list

    def get_comment(self, type_name: str) -> str:
        comment: str = ""
        for model in self.model_list:
            comment = comment + "{}: {}".format(
                model.curreny_name, getattr(model, type_name)
            )
            comment = comment + "\n"
        return comment

    def get_avg_val(self, type_name: str) -> float:
        match type_name:
            case "prfoit_lost":
                # 損益
                return statistics.mean([val.prfoit_lost for val in self.model_list])
            case "total_number_transactions":
                # 総取引数
                return statistics.mean(
                    [val.total_number_transactions for val in self.model_list]
                )
            case "profit_factor":
                # プロフィットファクタ
                return statistics.mean([val.profit_factor for val in self.model_list])
            case "expected_gain":
                # 期待利得
                return statistics.mean([val.expected_gain for val in self.model_list])
            case "drawdown_d":
                # ドローダウン $
                return statistics.mean([val.drawdown_d for val in self.model_list])
            case "drawdown_p":
                # ドローダウン %
                return statistics.mean([val.drawdown_p for val in self.model_list])

        return 0.0


def get_avg_data_model(model_list: list) -> GroupDataModel:
    model: GroupDataModel = GroupDataModel(model_list=model_list)
    return model


def load_mt4_html(filename_fullpath: str) -> bs4.BeautifulStoneSoup:
    file_path = Path(filename_fullpath)
    # win版のMT4で作成したhtmlファイルの文字コードはshift-jisになる
    with open(str(file_path), encoding="shift-jis") as f:
        soup: bs4.BeautifulStoneSoup = bs4.BeautifulSoup(f, "html.parser")

        return soup


def create_currency_name(filename_fullpath: str) -> str:
    file_path = Path(filename_fullpath)
    return file_path.stem.split("_")[0]


def create_model_list(currenty_name: str, soup: bs4.BeautifulStoneSoup) -> list:
    element_table = soup.find_all("table")

    # print(element_table)
    element_target_table = element_table[1]
    # print(element_target_table)

    element_target_table_soup = bs4.BeautifulStoneSoup = bs4.BeautifulSoup(
        str(element_target_table), "html.parser"
    )
    element_tr_list: list = element_target_table_soup.find_all("tr")
    del element_tr_list[0]

    data_model_list: list = list()
    for e in element_tr_list:
        e_soup: bs4.BeautifulStoneSoup = bs4.BeautifulSoup(str(e), "html.parser")
        td_list: list = e_soup.find_all("td")

        data_model_list.append(DataModel(curreny_name=currenty_name, html_list=td_list))

    return data_model_list


def create_group_model_dict(model_list: list[DataModel]) -> dict:
    group_model_dict: dict[str, list[DataModel]] = dict()

    count: int = 0
    for model in model_list:
        if not model.params in group_model_dict:
            group_model_dict[model.params] = list()

        group_model_dict[model.params].append(model)
        if count < len(group_model_dict[model.params]):
            count = len(group_model_dict[model.params])

    # 各要素の配列数が一番高い要素のみ抽出
    # 通貨の種類でそろっていないのは除外する(例: ドル円とポンドドルの2種類とドル円とユーロドルとオージドルの3種類なら3種類を採用)
    return dict(filter(lambda item: count <= len(item[1]), group_model_dict.items()))


def write_cell_ea_param(sheet, cell_name: str, model: GroupDataModel, param_name: str):
    if param_name == "params":
        sheet[cell_name] = model.params
    else:
        sheet[cell_name] = model.get_avg_val(type_name=param_name)
        # 小数点以下を2桁まで表示
        sheet[cell_name].number_format = "0.00"

        from openpyxl.comments import Comment

        # 各通貨の情報をコメントにする
        comment = Comment(model.get_comment(type_name=param_name), "Comment Author")
        comment.height = 200
        sheet[cell_name].comment = comment


def output_xlsx(dir_fullpath: str, filename: str, model_list: list[GroupDataModel]):
    file_path = Path(dir_fullpath) / "{}.xlsx".format(filename)
    file_path.unlink(True)

    # ブックを作成
    wb = openpyxl.Workbook()

    sheet = wb["Sheet"]
    header_list: list = [
        "NO",
        "損益",
        "総取引数",
        "プロフィットファクタ",
        "期待利得",
        "ドローダウン $",
        "ドローダウン %",
        "パラメータ",
    ]

    name_col: int = 1
    for name in header_list:
        sheet.cell(row=1, column=name_col, value=name)
        name_col = name_col + 1

    count: int = 2
    for model in model_list:
        count_str = str(count)
        sheet["A" + count_str] = str(count - 1)
        write_cell_ea_param(
            sheet=sheet,
            cell_name="B" + count_str,
            model=model,
            param_name="prfoit_lost",
        )
        write_cell_ea_param(
            sheet=sheet,
            cell_name="C" + count_str,
            model=model,
            param_name="total_number_transactions",
        )
        write_cell_ea_param(
            sheet=sheet,
            cell_name="D" + count_str,
            model=model,
            param_name="profit_factor",
        )
        write_cell_ea_param(
            sheet=sheet,
            cell_name="E" + count_str,
            model=model,
            param_name="expected_gain",
        )
        write_cell_ea_param(
            sheet=sheet, cell_name="F" + count_str, model=model, param_name="drawdown_d"
        )
        write_cell_ea_param(
            sheet=sheet, cell_name="G" + count_str, model=model, param_name="drawdown_p"
        )
        write_cell_ea_param(
            sheet=sheet, cell_name="H" + count_str, model=model, param_name="params"
        )

        count = count + 1
    # オートフィルタ範囲の設定
    sheet.auto_filter.ref = "{}:{}".format("A1", "G{}".format(count))

    # 保存
    wb.save(str(file_path))


def get_target_file_list(dir_filenamt: str) -> list:
    import glob

    file_fullpath: str = str(Path(dir_filenamt) / "*htm")

    return glob.glob(file_fullpath)


def create_param_fit_model_list(path_filename_list: list):
    model_list: list = list()
    for path_filename in path_filename_list:
        soup = load_mt4_html(path_filename)
        assert not soup is None

        currenty_name: str = create_currency_name(path_filename)
        model_list.extend(create_model_list(currenty_name=currenty_name, soup=soup))
        assert not model_list is None
        assert 0 < len(model_list)

    group_model_dict: dict = create_group_model_dict(model_list=model_list)
    assert not group_model_dict is None
    assert 0 < len(group_model_dict)

    avg_model_list: list[GroupDataModel] = list()
    for key, value in group_model_dict.items():
        # model: DataModel = get_avg_data_model(value)
        model: GroupDataModel = get_avg_data_model(value)
        avg_model_list.append(model)

    return avg_model_list


def main():
    pass


if __name__ == "__main__":
    main()
