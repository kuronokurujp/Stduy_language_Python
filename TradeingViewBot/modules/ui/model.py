#!/usr/bin/env python


# TODO: ツールのモデル
class Model(object):
    __title: str = "トレーディングビューボット"
    __size: tuple[int, int] = (1024, 728)

    @property
    def title(self) -> str:
        return self.__title

    @property
    def size(self) -> tuple[int, int]:
        return self.__size
