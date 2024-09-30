import abc
import modules.trade.engine_interface as trade_intarface
import modules.trade.analyzer_interface as analyzer_interface


class ILogic(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def analyzer_class(self) -> type[analyzer_interface.IAnalyzer]:
        raise NotImplementedError()

    @abc.abstractmethod
    def attach_test_strategy(self, trade_engine: trade_intarface.IEngine) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def attach_opt_strategy(self, trade_engine: trade_intarface.IEngine) -> int:
        raise NotImplementedError()
