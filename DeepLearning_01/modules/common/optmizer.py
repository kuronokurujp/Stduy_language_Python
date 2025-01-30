#!/usr/bin/env python
import numpy as np


# 確率的勾配降下法
class SGD:
    def __init__(self, lr=0.01):
        self.lr = lr

    def update(self, params, grads):
        for key in params.keys():
            params[key] -= self.lr * grads[key]


# モーメンタム
class Momentum:
    def __init__(self, lr=0.01, momentum=0.9):
        self.momentum = momentum
        self.lr = lr
        self.v = None

    def update(self, params, grads):
        if self.v is None:
            self.v = {}
            for k, v in params.items():
                self.v[k] = np.zeros_like(v)

        for k in params.keys():
            self.v[k] = self.momentum * self.v[k] - self.lr * grads[k]
            params[k] += self.v[k]


# AdaGrad
class AdaGrad:
    def __init__(self, lr=0.01):
        self.lr = lr
        self.h = None

    def update(self, params, grads):
        if self.h is None:
            self.h = {}
            for k, v in params.items():
                self.h[k] = np.zeros_like(v)

        for k in params.keys():
            self.h[k] += grads[k] * grads[k]
            # 0除算回避のため1e-7の最小値を加算
            params[k] -= self.lr * grads[k] / (np.sqrt(self.h[k]) + 1e-7)


class Adam:
    def __init__(self, lr=0.001, beta1=0.9, beta2=0.999):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.iter = 0
        self.m = None
        self.v = None

    def update(self, params, grads):
        if self.m is None:
            self.m = {}
            self.v = {}
            for k, v in params.items():
                self.m[k] = np.zeros_like(v)
                self.v[k] = np.zeros_like(v)

        self.iter += 1
        # 学習率を計算
        # 更新するたびに指数が増える
        lr_t = (
            self.lr
            * np.sqrt(1.0 - self.beta2**self.iter)
            / (1.0 - self.beta1**self.iter)
        )

        for k in params.keys():
            # モーメントと速度を更新
            self.m[k] += (1 - self.beta1) * (grads[k] - self.m[k])
            self.v[k] += (1 - self.beta2) * (grads[k] ** 2 - self.v[k])

            # AdaGradの計算式
            params[k] -= lr_t * self.m[k] / (np.sqrt(self.v[k]) + 1e-7)
