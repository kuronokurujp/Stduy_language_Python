import abc
import configparser
import pathlib
import modules.strategy.interface.analyzer_interface as analyzer_interface


class IModel(metaclass=abc.ABCMeta):

    # 通常検証モードか
    @abc.abstractmethod
    def is_strategy_mode(self):
        raise NotImplementedError()

    # テストの資金
    @abc.abstractmethod
    def get_cash(self):
        raise NotImplementedError()

    # ロジックのパラメータ名の値を取得
    @abc.abstractmethod
    def get_param(self, name: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def output_strategy(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        raise NotImplementedError()


# ロジックファイルをロードしたロジック基本クラス
class IniFileBaseModel(IModel):
    # ConfigParserオブジェクトを作成
    __config = configparser.ConfigParser()
    __cash: int = 0

    def __init__(self, logic_filepath: pathlib.Path, cash: int) -> None:
        # INIファイルを読み込む
        # UTF-8エンコーディングでファイルを読み込む
        with open(logic_filepath, "r", encoding="utf-8") as configfile:
            self.__config.read_file(configfile)

        self.__cash = cash

    # 通常検証モードかどうか
    def is_strategy_mode(self):
        try:
            self.get_param("test")
        except Exception as identifier:
            return False

        return True

    # テストの資金
    def get_cash(self):
        return self.__cash

    def get_param(self, name: str):
        return self.__config[name]

    def output_strategy(self) -> int:
        return 0

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        pass
