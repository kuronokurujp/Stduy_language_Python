#!/usr/bin/env python


# TODO: ツールのモデル
class Model(object):
    __title: str = "トレーディングビューボット"
    __size: tuple[int, int] = (512, 364)

    @property
    def title(self) -> str:
        return self.__title

    @property
    def size(self) -> tuple[int, int]:
        return self.__size
