#!/usr/bin/env python
import abc
import pathlib
import modules.model.market.market_intareface as market_interface
import modules.model.controller.model as logic_interface


class IController(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(
        self, logic_model: logic_interface, chart_model: market_interface.IModel
    ) -> None:
        return NotImplementedError()

    @abc.abstractmethod
    def save_file(self, filepath: pathlib.Path):
        return NotImplementedError()
