#!/usr/bin/env python
import abc


class IView(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def log(self, msg: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def begin_draw(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def draw(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def end_draw(self) -> None:
        raise NotImplementedError()
