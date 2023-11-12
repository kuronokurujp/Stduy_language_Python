import modules.log.logger
import app.controller
import app.model

def test_ui_open():
    app_model = app.model.Model()
    app_ctrl = app.controller.Controller(model=app_model, logger=modules.log.logger.PrintLogger())
    app_ctrl.open()

    assert True
