#!/usr/bin/env python
import abc
import pathlib
import modules.chart.model_intareface as chart_interface
import modules.logics.logic_interface as logic_interface


class IEngine(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(self, logic: logic_interface, chart_model: chart_interface.IModel) -> None:
        return NotImplementedError()

    @abc.abstractmethod
    def save_file(self, filepath: pathlib.Path):
        return NotImplementedError()
