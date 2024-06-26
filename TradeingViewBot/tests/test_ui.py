#!/usr/bin/env python
import modules.log.logger
import modules.ui.model
import modules.ngrok.interface
import modules.ngrok.model
import modules.ngrok.controller

import app.controller
import app.model


class DummyNgrokController(modules.ngrok.interface.INgrokController):
    def run(self) -> tuple[bool, str]:
        return (True, "")

    def cmd_start_listen(self) -> tuple[bool, str]:
        return (True, "")

    def cmd_stop_listen(self) -> tuple[bool, str]:
        return (True, "")

    def get_url(self) -> str:
        return ""

    def do_post(self, req_body_json: dict):
        pass


def test_ui_open():
    model_config: app.model.ModelConfig = app.model.ModelConfig()
    app_model = app.model.Model(config=model_config, b_debug=True)
    app_ctrl = app.controller.Controller(
        model=app_model, logger=modules.log.logger.PrintLogger()
    )
    app_ctrl.open()

    assert True


class TestUICtrl02(app.controller.Controller):
    count: int = 0

    def _create_ngrok_ctrl(
        self,
        model: modules.ngrok.model.Model,
    ) -> modules.ngrok.interface.INgrokController:
        return DummyNgrokController()

    def event_open(self):
        super().event_open()

    def event_update(self):
        if self.count <= 30:
            self.view.enable_trade(b_enable=False)

        elif 60 <= self.count:
            self.view.enable_trade(b_enable=True)

            if 120 <= self.count:
                self.count = 0

        self.count = self.count + 1


def test_ui_btn_run_trade_enable():
    model_config: app.model.ModelConfig = app.model.ModelConfig()
    app_model = app.model.Model(config=model_config, b_debug=True)
    app_ctrl = TestUICtrl02(model=app_model, logger=modules.log.logger.PrintLogger())
    app_ctrl.open()

    assert True
