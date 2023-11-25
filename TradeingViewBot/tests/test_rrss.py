from modules.broker.rrss import controller
from modules.broker.rrss import model
from pathlib import Path


# test rrss excel file open / close
def test_rrss_excel_file_open_close():
    rrss_model: model.Model = model.Model(
        config_tomlfile_path=Path("data/config/rrss.toml")
    )
    rrss_ctrl: controller.Controller = controller.Controller(model=rrss_model)
    try:
        bRet, msg = rrss_ctrl.open()
        print(msg)
        assert bRet

        bRet, msg = rrss_ctrl.close()
        print(msg)
        assert bRet
    except Exception as ex:
        print(ex)
        assert False

# test rrss excel file open / close
def test_rrss_excel_file_open_close_v2():
    rrss_model: model.Model = model.Model(
        config_tomlfile_path=Path("data/config/rrss.toml")
    )
    rrss_ctrl: controller.Controller = controller.Controller(model=rrss_model)
    try:
        bRet, msg = rrss_ctrl.open()
        print(msg)
        assert bRet

        # 起動中にエクセルファイルを手動で閉じた後にコードで閉じるとエラーになる
        import time
        time.sleep(10)

        bRet, msg = rrss_ctrl.close(bSave=True)
        print(msg)
        assert bRet
    except Exception as ex:
        print(ex)
        assert False
