#!/usr/bin/env python
# スレッドやコルーチンの動作検証用


def test_async():
    import asyncio
    import threading

    async def greet_every_first_seconds():
        while True:
            print("first")
            await asyncio.sleep(2)

    class A(object):

        def __init__(self, num) -> None:
            self.__num = num

        def _between_callback(self, msg, look):
            with look:

                loop = asyncio.new_event_loop()

                loop.run_until_complete(self.greet_every_two_seconds(self.__num))
                loop.close()

        async def greet_every_two_seconds(self, msg):
            while True:
                print("{}".format(msg))
                await asyncio.sleep(2)

    a = A(num=10)
    b = A(num=20)
    c = A(num=30)
    semaphore = threading.BoundedSemaphore(64)
    _thread = threading.Thread(target=a._between_callback, args=("thread0", semaphore))
    _thread1 = threading.Thread(target=b._between_callback, args=("thread1", semaphore))
    _thread2 = threading.Thread(target=c._between_callback, args=("thread2", semaphore))
    # スレッドのブロッキングはしない
    _thread.daemon = True
    _thread1.daemon = True
    _thread2.daemon = True
    _thread.start()
    _thread1.start()
    _thread2.start()

    asyncio.run(greet_every_first_seconds())

    # スレッドが稼働している
    while _thread.is_alive():
        pass
