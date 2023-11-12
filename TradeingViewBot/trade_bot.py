import app.controller
import app.model
import modules.log.logger

if __name__ == "__main__":
    app_model = app.model.Model()
    app_ctrl = app.controller.Controller(model=app_model, logger=modules.log.logger.PrintLogger())
    app_ctrl.open()

