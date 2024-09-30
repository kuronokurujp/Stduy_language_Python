import modules.chart.model.logic.model as model
import modules.trade.interface.analyzer_interface as analyzer_interface
import modules.trade.interface.engine_interface as engine_interface
import pathlib


# テストロジックのモデル
class IniFileModelByTest(model.IniFileBaseModel):
    def __init__(
        self,
        logic_filepath: pathlib.Path,
        # 戦略を登録するメソッド
        regist_strategey,
        # 解析を登録するメソッド
        regist_analyzer,
    ) -> None:
        super().__init__(logic_filepath=logic_filepath)
        self.__regist_strategy_func = regist_strategey
        self.__regist_analyzer_func = regist_analyzer

    def output_strategy(self, engine: engine_interface.IEngine) -> int:
        self.__regist_strategy_func(engine.cerebro, self.get_param("test"))
        return 0

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return self.__regist_analyzer_func()


# 最適化ロジックのモデル
class IniFileModelByOpt(model.IniFileBaseModel):

    def __init__(
        self,
        logic_filepath: pathlib.Path,
        # 最適化戦略を登録するメソッド
        regist_opt,
    ) -> None:
        super().__init__(logic_filepath=logic_filepath)
        self.__regist_opt_func = regist_opt

    def output_strategy(self, engine: engine_interface.IEngine) -> int:
        return self.__regist_opt_func(engine.cerebro, self.get_param("opt"))

    def analayzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        return None
