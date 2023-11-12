#!/usr/bin/env python
from abc import ABC, abstractmethod


# TODO: ngrokの制御インターフェイス
class INgrokController(ABC):
    @abstractmethod
    def run(self) -> tuple[bool, str]:
        raise NotImplementedError()

    @abstractmethod
    def cmd_start_listen(self) -> tuple[bool, str]:
        raise NotImplementedError()

    @abstractmethod
    def cmd_stop_listen(self) -> tuple[bool, str]:
        raise NotImplementedError()

    @abstractmethod
    def get_url(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def do_post(self, req_body_json: dict):
        raise NotImplementedError()
