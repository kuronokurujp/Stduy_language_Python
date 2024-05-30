#!/usr/bin/env python
import asyncio
from modules.log.logger import AppLogger
import modules.ngrok.interface
import threading
import json
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import modules.ngrok.model
import ngrok
from urllib.parse import parse_qs, urlparse


#
class NgrokHTTPServer(ThreadingHTTPServer):
    _controller = None

    def __init__(
        self,
        server_address,
        RequestHandlerClass,
        bind_and_activate=True,
        controller=None,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

        self._controller = controller


#
class NgrokHttpRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        ctrl: Controller = None
        ngrok_server: NgrokHTTPServer = self.server
        if ngrok_server is not None:
            ctrl = ngrok_server._controller

        if ctrl.logger is not None:
            ctrl.logger.info("path = {}".format(self.path))
            ctrl.logger.info("headers\r\n-----\r\n{}-----".format(self.headers))
        else:
            print("path = {}".format(self.path))
            print("headers\r\n-----\r\n{}-----".format(self.headers))

        parsed_path = urlparse(self.path)

        if ctrl.logger is not None:
            ctrl.logger.info(
                "parsed: path = {}, query = {}".format(
                    parsed_path.path, parse_qs(parsed_path.query)
                )
            )
            ctrl.logger.info("headers\r\n-----\r\n{}-----".format(self.headers))
        else:
            print(
                "parsed: path = {}, query = {}".format(
                    parsed_path.path, parse_qs(parsed_path.query)
                )
            )
            print("headers\r\n-----\r\n{}-----".format(self.headers))

        content_length = int(self.headers["content-length"])

        # Bodyを取得
        req_body: str = self.rfile.read(content_length).decode("utf-8")

        if ctrl.logger is not None:
            ctrl.logger.info("body = {}".format(req_body))
        else:
            print("body = {}".format(req_body))

        if ctrl is not None:
            ctrl.do_post(json.loads(req_body))

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"")


# ngrokを制御するクラス
class Controller(modules.ngrok.interface.INgrokController):
    # このモデルは初期化後にも変更可能
    __model: modules.ngrok.model.Model = None
    __ngrok_listener: ngrok.Listener = None
    __server: ThreadingHTTPServer = None
    __server_thread: threading = None
    __logger: AppLogger = None

    @property
    def logger(self) -> AppLogger:
        return self.__logger

    def __init__(
        self, model: modules.ngrok.model.Model, logger: AppLogger = None
    ) -> None:
        self.__model = model
        self.__logger = logger

    def __del__(self):
        pass

    # ngrokを実行する
    def run(self) -> tuple[bool, str]:
        bRet: bool = False
        msg: str = ""
        try:
            # Auth設定
            bRet, msg = self.cmd_add_authtoken()
            if bRet == False:
                raise Exception(msg)

        except Exception as ex:
            msg = ex
            bRet = False
        finally:
            return bRet, msg

    # ngrokのhttp通知の受け取りを開始
    def cmd_start_listen(self) -> tuple[bool, str]:
        bRet: bool = False
        msg: str = ""

        if self.__logger is not None:
            self.__logger.info("start ngrok")

        if self.__ngrok_listener is not None:
            self.cmd_stop_listen()

        try:
            self.__ngrok_listener = ngrok.forward(
                "localhost:{}".format(self.__model.http_port),
                authtoken=self.__model.token,
                prot="http",
            )
            self.__server = NgrokHTTPServer(
                ("localhost", self.__model.http_port),
                NgrokHttpRequestHandler,
                controller=self,
            )

            # TODO: 以下を呼ぶと例外エラー(ERR_NGROK_4018)になる
            # self.__ngrok_listener = ngrok.listen(self.__server)

            # TODO: ロックはつけなくてもいいの？
            self.__server_thread = threading.Thread(target=self.__server.serve_forever)
            self.__server_thread.daemon = True
            self.__server_thread.start()

            if self.__logger is not None:
                self.__logger.info("webhook url: {}".format(self.get_url()))

            bRet = True
        except Exception as ex:
            if self.__logger is not None:
                self.__logger.err("{}".format(ex))

            if self.__ngrok_listener is not None:
                self.cmd_stop_listen()

            bRet = False
            msg = ex

        return bRet, msg

    # ngrokのhttp通知の受け取りを終了
    def cmd_stop_listen(self) -> tuple[bool, str]:
        # この呼び方をしないと以下のエラーが出た
        # 理由不明
        # RuntimeError: Event loop is closed
        return asyncio.run(self.__cmd_stop_listen())

    def get_url(self) -> str:
        if self.__ngrok_listener is None:
            return ""

        return self.__ngrok_listener.url()

    def do_post(self, req_body_json: dict):
        if self.__logger is not None:
            self.__logger.info("post {}".format(req_body_json))
        # TODO: コールバックを呼ぶ

    # ngrokのhttp通知の受け取りを終了
    async def __cmd_stop_listen(self) -> tuple[bool, str]:
        if self.__logger is not None:
            self.__logger.info("stop ngrok")

        bRet: bool = False
        msg: str = ""
        try:
            bRet = True
            if self.__server is not None:
                self.__server.shutdown()
            self.__server = None

            if self.__ngrok_listener is not None:
                # await self.__ngrok_listener.close()

                # 実行すると以下のエラーが出た
                ngrok.disconnect(self.__ngrok_listener.url())

            ngrok.kill()

            self.__ngrok_listener = None

        except Exception as ex:
            if self.__logger is not None:
                self.__logger.err("stop ngrok {}".format(ex))

            bRet = False
            msg = ex
        finally:
            return bRet, msg
