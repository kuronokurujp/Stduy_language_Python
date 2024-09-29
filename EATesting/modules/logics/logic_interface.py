import abc
import modules.trade.engine_interface as trade_intarface


class ilogic(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def attach_test_strategy(self, trade_engine: trade_intarface.iengine) -> None:
        return NotImplementedError()

    @abc.abstractmethod
    def attach_opt_strategy(self, trade_engine: trade_intarface.iengine) -> int:
        return NotImplementedError()
