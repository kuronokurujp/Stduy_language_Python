from modules.ngrok import controller, model
from pathlib import Path

# test start and stop listen
def test_start_and_stop_listen():
    ngrok_model: model.Model = model.Model(
        config_tomlfile_path=Path("data/config/ngrok.toml")
    )
    ngrok_ctrl: controller.Controller = controller.Controller(model=ngrok_model)

    bRet, msg = ngrok_ctrl.cmd_start_listen()
    print(msg)
    assert bRet

    bRet, msg = ngrok_ctrl.cmd_stop_listen()
    print(msg)
    assert bRet


# test client
def test_client_listen():
    ngrok_model: model.Model = model.Model(
        config_tomlfile_path=Path("data/config/ngrok.toml")
    )
    ngrok_ctrl: controller.Controller = controller.Controller(model=ngrok_model)

    bRet, msg = ngrok_ctrl.cmd_start_listen()
    print(msg)
    assert bRet

    bRet, msg = ngrok_ctrl.cmd_stop_listen()
    print(msg)
    assert bRet


# test webhook request
def test_webhook_request():
    ngrok_model: model.Model = model.Model(
        config_tomlfile_path=Path("data/config/ngrok.toml")
    )
    ngrok_ctrl: controller.Controller = controller.Controller(model=ngrok_model)

    bRet, msg = ngrok_ctrl.cmd_start_listen()
    print(msg)
    assert bRet

    import requests
    import json

    webhook_url = ngrok_ctrl.get_url()
    print(webhook_url)

#    data = {"名前": "テスト太郎", "性別": "男性", "URL": "https://dummy"}
# フォーマットは下記でいい
    data = {"名称":"@RRSS, @{{ticker}} で @{{strategy.order.action}} @{{strategy.order.contracts}} 約定。新しいポジは @{{strategy.position_size}}"}
    r = requests.post(
        webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    import time
    time.sleep(10)

    bRet, msg = ngrok_ctrl.cmd_stop_listen()
    print(msg)
    assert bRet
