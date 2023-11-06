#!/usr/bin/env python
import modules.ui.model
import modules.ui.view
from modules.log.logger import AppLogger

# TODO: ツール画面の制御
class Controller(object):
    __view: modules.ui.view.View = None
    __model: modules.ui.model.Model = None
    __logger: AppLogger = None

    def __init__(self, model: modules.ui.model.Model, logger: AppLogger = None) -> None:
        self.__model = model
        self.__view = modules.ui.view.View(self.__model.title, self.__model.size)
        self.__logger = logger

    def open(self):
        self.__view.open()
