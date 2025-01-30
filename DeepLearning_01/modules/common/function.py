#!/usr/bin/env python
import numpy as np


# 活性化関数一覧
# 何もしない活性関数
def identity(x):
    return x


# ステップ活性関数
def step(x):
    return np.array(x > 0, dtype=int)


# シグモイド活性関数
def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


# ReLU活性関数
def relu(x):
    return np.maximum(0.0, x)


def tanh(x):
    return np.tanh(x)


# ソフトマックス活性関数
# 計算精度が悪い版
def softmax_bad(x):
    exp_a = np.exp(x)
    sum_exp_a = np.sum(exp_a)
    return exp_a / sum_exp_a


# ソフトマックス活性関数
def softmax(a):
    # 配列の中で最大値を定数値とする
    # 2次元以上の場合は各次元の最大値を求める
    max = np.max(a, axis=-1, keepdims=True)
    exp_a = np.exp(a - max)

    # 1次元の時は次元を意識した計算はしない
    if exp_a.ndim == 1:
        sum_exp_a = np.sum(exp_a, keepdims=True)
    else:
        sum_exp_a = np.sum(exp_a, axis=1, keepdims=True)

    return exp_a / sum_exp_a


# 損失関数一覧
# 2乗和誤差
def mean_squared_error(y, t):
    return 0.5 * np.sum((y - t) ** 2)


# 交差エントロピー誤差
def cross_entropy_error(y, t):
    # 10のマイナス7乗を補正値にしている
    delta = 1e-7
    return -np.sum(t * np.log(y + delta))


# 交差エントロピー誤差(バッチ対応版)
# 入力した訓練データを内部で調整してエラーにならいように計算できるようにしている
def cross_entropy_error_batch(x_train, t_train):
    if x_train.ndim == 1:
        # 1次元配列を2次元配列にしてバッチで計算できる形状に変えている
        t_train = t_train.reshape(1, t_train.size)
        x_train = x_train.reshape(1, x_train.size)

    # 入力データと教師データの形状が一致した場合は
    # 教師データを正解ラベルが1で後は0になるone-hotのデータに変換
    if t_train.size == x_train.size:
        t_train = t_train.argmax(axis=1)

    # 10のマイナス7乗を補正値にしている
    # これを入れないと出力がnanになるケースがある
    delta = 1e-7
    batch_size = x_train.shape[0]
    return -np.sum(np.log(x_train[np.arange(batch_size), t_train] + delta)) / batch_size
