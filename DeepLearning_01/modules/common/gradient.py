#!/usr/bin/env python
import numpy as np


# 微分の悪い計算
def numerical_diff_bad(f, x):
    # 10のマイナス50乗ではマシンで扱えないので0になる
    # 分母が0になるので必ず0が出力される
    h = 1e-50
    return (f(x + h) - f(x)) / h


# 微分の計算
def numerical_diff(f, x):
    h = 1e-4
    # 数値差分で計算している
    return (f(x + h) - f(x - h)) / (2 * h)


def _numerical_gradient_1d(f, x):
    h = 1e-4
    grad = np.zeros_like(x)

    for idx in range(x.size):
        tmp_val = x[idx]
        x[idx] = tmp_val + h
        fxh1 = f(x)

        x[idx] = tmp_val - h
        fxh2 = f(x)

        grad[idx] = (fxh1 - fxh2) / (2 * h)
        x[idx] = tmp_val

    return grad


# 微分計算で勾配
def numerical_gradient_2d(f, x):
    if x.ndim == 1:
        # 配列が1次元なら1次元用の処理を使う
        return _numerical_gradient_1d(f, x)

    grad = np.zeros_like(x)
    for idx, _x in enumerate(x):
        grad[idx] = _numerical_gradient_1d(f, _x)

    return grad


# 勾配降下法の計算
def gradient_descent(f, init_x, lr=0.01, step_num=100):
    x = init_x.copy()
    # 計算過程のリスト
    x_history = []

    for i in range(step_num):
        x_history.append(x.copy())

        grad = numerical_gradient_2d(f, x)
        x -= lr * grad

    return x, np.array(x_history)


def numerical_gradient(f, x):
    h = 1e-4
    grad = np.zeros_like(x)

    # これを使う事で異なる次元の配列を共通した処理で扱う事が出来る
    # https://snowtree-injune.com/2020/06/29/nditer-z009/
    it = np.nditer(x, flags=["multi_index"], op_flags=["readwrite"])
    # 全要素で微分計算をする
    # 要素数が膨大だと処理終了に時間がかかるので注意
    while not it.finished:
        idx = it.multi_index
        tmp_val = x[idx]
        x[idx] = tmp_val + h
        fxh1 = f(x)

        x[idx] = tmp_val - h
        fxh2 = f(x)

        grad[idx] = (fxh1 - fxh2) / (2 * h)
        x[idx] = tmp_val
        it.iternext()

    return grad
