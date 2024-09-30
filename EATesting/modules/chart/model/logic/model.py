import abc
import configparser
import pathlib
import modules.trade.interface.engine_interface as engine_interface
import modules.trade.interface.analyzer_interface as analyzer_interface


class IModel(metaclass=abc.ABCMeta):

    # ロジックのパラメータ名の値を取得
    @abc.abstractmethod
    def get_param(self, name: str):
        raise NotImplementedError()

    @abc.abstractmethod
    def output_strategy(self, engine: engine_interface.IEngine) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        raise NotImplementedError()


# ロジックファイルをロードしたロジック基本クラス
class IniFileBaseModel(IModel):
    # ConfigParserオブジェクトを作成
    __config = configparser.ConfigParser()

    def __init__(self, logic_filepath: pathlib.Path) -> None:
        # INIファイルを読み込む
        # UTF-8エンコーディングでファイルを読み込む
        with open(logic_filepath, "r", encoding="utf-8") as configfile:
            self.__config.read_file(configfile)

    def get_param(self, name: str):
        return self.__config[name]

    def output_strategy(self, engine: engine_interface.IEngine) -> int:
        return 0

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        pass
