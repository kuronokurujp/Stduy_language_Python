import ngrok.model

# TODO: ngrokを制御するクラス
class Controller(object):
    # このモデルは初期化後にも変更可能
    __ctrl_model: ngrok.model.CtrlModel
    __config_model: ngrok.model.ConfigModel

    def __init__(self, ctrl_model: ngrok.model.CtrlModel, config_model: ngrok.model.ConfigModel) -> None:
        self.__ctrl_model = ctrl_model
        self.__config_model = config_model

    # ngrokを実行する
    def run(self):
        pass

