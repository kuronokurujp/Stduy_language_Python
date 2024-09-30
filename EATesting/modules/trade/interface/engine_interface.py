#!/usr/bin/env python
import abc
import pathlib
import modules.chart.model.market.market_intareface as market_interface
import modules.chart.model.logic.model as logic_interface


class IEngine(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(
        self, logic_model: logic_interface, chart_model: market_interface.IModel
    ) -> None:
        return NotImplementedError()

    @abc.abstractmethod
    def save_file(self, filepath: pathlib.Path):
        return NotImplementedError()
