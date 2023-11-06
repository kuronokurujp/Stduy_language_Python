import modules.ui.model
import modules.ui.view
import modules.ui.controller

def test_ui_open():
    ui_model = modules.ui.model.Model()
    ui_ctrl = modules.ui.controller.Controller(model=ui_model)
    ui_ctrl.open()

    assert True
