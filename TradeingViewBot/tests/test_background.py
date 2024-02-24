import threading
import modules.background.thread as bk_thread
import time
import asyncio


class TestMainThreadCallbackObject(object):
    __count: int = 0

    def __init__(self, count: int) -> None:
        self.__count = count

    def callback(self, no: int):
        print("callback: count({}) / no({})".format(self.__count, no))


class TestObject(bk_thread.NodeCallback):
    __no: int = 0
    __callback: TestMainThreadCallbackObject

    def start_thread(self, lock: threading.RLock):
        print("start: no({}): loop".format(self.__no))
        time.sleep(10)
        print("start2: no({}): loop".format(self.__no))
        with lock:
            self.__callback.callback(self.__no)

    def run_thread(self, lock: threading.RLock) -> bool:
        print("run: no({}): loop".format(self.__no))
        return True

    def end_thread(self, lock: threading.RLock):
        print("end: no({}): loop".format(self.__no))
        time.sleep(1)
        print("final end: no({}): loop".format(self.__no))

    def error_thread(self, ex: Exception, lock: threading.RLock):
        print("ex({})".format(ex))

    def __init__(self, no: int, callback: TestMainThreadCallbackObject) -> None:
        self.__no = no
        self.__callback = callback


# メインスレッドで生成したオブジェクトのコールバックを作成したスレッドの呼び出しと併せて呼び出せるか
def test_background():
    manger = bk_thread.Manager()

    test_list: list[TestObject] = list[TestObject]()
    callback: TestMainThreadCallbackObject = TestMainThreadCallbackObject(count=1)
    for i in range(2):
        test: TestObject = TestObject(no=i, callback=callback)
        id: int = manger.create(callback=test)
        test_list.append(test)

    while manger.is_threads:
        time.sleep(0.2)

        # ノードを一つずつ消して一つも残さずに消せるか
        id: int = manger.id_array[0]
        asyncio.run(manger.async_delete(id=id))


class TestObject02(bk_thread.NodeCallback):
    __manager: bk_thread.Manager = None
    __id: int = 0

    def start_thread(self, lock: threading.RLock):
        print("start:({})".format(self.__id))

    def run_thread(self, lock: threading.RLock) -> bool:
        return True

    def end_thread(self, lock: threading.RLock):
        print("end:({})".format(self.__id))

    def error_thread(self, ex: Exception, lock: threading.RLock):
        pass

    def __init__(self, manager: bk_thread.Manager) -> None:
        self.__manager = manager
        self.__id = self.__manager.create(callback=self)


# クラスのメソッドでスレッドを一時停止できるか
def test_background02():
    manger = bk_thread.Manager()

    TestObject02(manager=manger)
    TestObject02(manager=manger)
    TestObject02(manager=manger)

    while manger.is_threads:
        time.sleep(10)
        asyncio.run(manger.async_all_delete())
