#!/usr/bin/env python
import abc
import modules.model.market.interface as market_model_interface
import modules.model.controller.model as ctrl_interface
import modules.view.interface as view_interface


class IController(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def run(
        self,
        controller_model: ctrl_interface.IModel,
        chart_model: market_model_interface.IModel,
        view: view_interface.IView,
    ) -> None:
        return NotImplementedError()
