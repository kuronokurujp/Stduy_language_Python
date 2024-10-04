import modules.model.controller.model as model
import modules.strategy.interface.analyzer_interface as analyzer_interface
import pathlib
import backtrader as bt


# テストロジックのモデル
class IniFileModelByTest(model.IniFileBaseModel):

    @property
    def Cerebro(self) -> bt.Cerebro:
        return self.__cerebro

    def __init__(
        self,
        logic_filepath: pathlib.Path,
        cash: int,
        # 戦略を登録するメソッド
        regist_strategey,
        # 解析を登録するメソッド
        regist_analyzer,
    ) -> None:
        super().__init__(logic_filepath=logic_filepath, cash=cash)
        self.__regist_strategy_func = regist_strategey
        self.__regist_analyzer_func = regist_analyzer

        # Cerebroの初期化
        self.__cerebro = bt.Cerebro()

    def output_strategy(self) -> int:
        self.__regist_strategy_func(self.__cerebro, self.get_param("test"))
        return 0

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return self.__regist_analyzer_func()


# 最適化ロジックのモデル
class IniFileModelByOpt(model.IniFileBaseModel):

    def __init__(
        self,
        logic_filepath: pathlib.Path,
        cash: int,
        # 最適化戦略を登録するメソッド
        regist_opt,
    ) -> None:
        super().__init__(logic_filepath=logic_filepath, cash=cash)
        self.__regist_opt_func = regist_opt
        # Cerebroの初期化
        self.__cerebro = bt.Cerebro()

    def output_strategy(self) -> int:
        return self.__regist_opt_func(self.__cerebro, self.get_param("opt"))

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return None
