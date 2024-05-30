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
    # URLに別のパスを追加することができる
    webhook_url = "{}/25f4b493-85fe-11ee-92c2-7c7635fff5e0".format(webhook_url)
    print(webhook_url)

    #    data = {"名前": "テスト太郎", "性別": "男性", "URL": "https://dummy"}
    # フォーマットは下記でいい
    data = {
        # シンボルのティッカー(AAPLなど日経MiniならNK225M1!)
        "ticker": "{{ticker}}",
        # 注文コメント
        "comment": "{{strategy.order.comment}}",
        # アラートメッセージ
        "alert_message": "{{strategy.order.alert_message}}",
        # 戦略キー(アプリ用)
        "strategy_key": "Fnt5w7HjaJKdTrtMjnirjnHf",
        # 注文時の価格
        "price": "{{strategy.order.price}}",
        # 注文時の文字列(buy / sell)
        "action": "{{strategy.order.action}}",
        # 注文の取引数
        "contracts": "{{strategy.order.contracts}}",
        # ポジションサイズ
        "pos_size": "{{strategy.position_size}}"
    }
    r = requests.post(
        webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"}
    )

    import time

    time.sleep(10)

    bRet, msg = ngrok_ctrl.cmd_stop_listen()
    print(msg)
    assert bRet
