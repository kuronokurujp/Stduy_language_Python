#!/usr/bin/env python
import tkinter as tk
from tkinter import messagebox


# 処理終了時のアラート表示
def show_alert(title: str, msg: str):
    # ベル音
    print("\a")

    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning(title=title, message=msg)


# 開始値、終了値、ステップ値に浮動小数点数値を受け取る関数の定義
def frange(start, end, step):
    if step == 0:
        raise ValueError("step must not be zero")

    start = float(start)
    end = float(end)
    step = float(step)

    # range関数と同様な振る舞いにする
    if abs(step) > abs(start - end):
        return [start]
    if step > 0 and end - start < 0:
        return []
    elif step < 0 and end - start > 0:
        return []

    exp = len(str(step).split(".")[1])  # 丸める際に使用する桁数
    result = [start]
    val = start
    if step > 0:
        while (val := round(val + step, exp)) < end:
            result.append(val)
    else:
        while (val := round(val + step, exp)) > end:
            result.append(val)
    return result
