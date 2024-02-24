#!/usr/bin/env python
import threading
from concurrent.futures import ThreadPoolExecutor, Future
import time
from abc import ABC, abstractmethod
import asyncio


# コールバック用のインターフェイス
# 排他制御は呼び出し側である
# システム内でやる排他制御範囲が大きくて排他しなくてもいい箇所まで排他してしまうから
# 排他すると排他しているスレッド以外は停止するのでできるだけ停止させないために使う側が排他する
# 排他するかどうかは別スレッドでも変数の書き込みがあるかどうか
class NodeCallback(ABC):
    @abstractmethod
    def start_thread(self, lock: threading.RLock):
        raise NotImplementedError()

    @abstractmethod
    def run_thread(self, lock: threading.RLock) -> bool:
        raise NotImplementedError()
        return False

    @abstractmethod
    def end_thread(self, lock: threading.RLock):
        raise NotImplementedError()

    @abstractmethod
    def error_thread(self, ex: Exception, lock: threading.RLock):
        raise NotImplementedError()


def _worker_thread(
    lock: threading.RLock, callback: NodeCallback, finished: threading.Event
):
    bRunning: bool = True
    try:
        callback.start_thread(lock=lock)
        while bRunning and not finished.is_set():
            bRunning = callback.run_thread(lock=lock)
            time.sleep(0.01)
    except Exception as ex:
        callback.error_thread(ex, lock=lock)
    finally:
        # 終了後の呼び出し
        callback.end_thread(lock=lock)


# バックグラウンドスレッド管理
class Manager(object):
    __thread_dict: dict[int, (Future, threading.Event)] = dict[
        int, (Future, threading.Event)
    ]()
    __lock: threading.RLock = threading.RLock(time=0.1)
    __executor: ThreadPoolExecutor = None

    # スレッドがあるか
    @property
    def is_threads(self) -> bool:
        if len(self.__thread_dict) <= 0:
            return False

        return True

    # 存在するスレッドの全IDを配列
    @property
    def id_array(self) -> list[int]:
        return list[int](self.__thread_dict.keys())

    def __init__(self) -> None:
        self.__executor = ThreadPoolExecutor(max_workers=32)

    # スレッド作成
    def create(self, callback: NodeCallback) -> int:
        finished = threading.Event()
        future: Future = self.__executor.submit(
            _worker_thread, self.__lock, callback, finished
        )

        obj_id: int = id(future)

        self.__thread_dict[obj_id] = (future, finished)
        return obj_id

    # スレッド削除
    async def async_delete(self, id: int):
        if id not in self.__thread_dict:
            return

        # 処理を終了
        finished: threading.Event = self.__thread_dict[id][1]
        finished.set()

        future: Future = self.__thread_dict[id][0]
        # 処理は走っている間は待機
        while future.running():
            await asyncio.sleep(0.01)

        # キャンセル
        future.cancel()

        # 破棄まで待つ
        while not future.done():
            await asyncio.sleep(0.01)

        del self.__thread_dict[id]

    # ノードを全削除
    async def async_all_delete(self):
        task_list = list()
        for id, node in self.__thread_dict.items():
            task_list.append(self.async_delete(id=id))

        async with asyncio.TaskGroup() as tg:
            for task in task_list:
                tg.create_task(task)
