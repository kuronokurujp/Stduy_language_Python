#!/usr/bin/env python
import numpy as np
import modules.common.function as function
import modules.common.util as util


# 活性関数Reluの順伝搬と逆伝搬の計算をする
class Relu:
    def __init__(self):
        self.mask = None

    def forward(self, x, train_flg: bool = False):
        self.mask = x <= 0
        out = x.copy()
        out[self.mask] = 0
        return out

    def backward(self, dout):
        dout[self.mask] = 0
        dx = dout
        return dx


# 活性関数Sigmoidの順伝搬と逆伝搬の計算
class Sigmoid:
    def __init__(self):
        self.out = None

    def forward(self, x, train_flg: bool = False):
        out = 1.0 / (1.0 + np.exp(-x))
        self.out = out
        return out

    def backward(self, dout):
        dx = dout * (1.0 - self.out) * self.out
        return dx


# Tanhの順伝搬と逆伝搬
class Tanh:
    def __init__(self):
        self.out = None

    def forward(self, x, train_flg: bool = False):
        out = np.tanh(x)
        self.out = out
        return out

    def backward(self, dout):
        dx = 1.0 - self.out**2
        return dout * dx


# アフィン変換の順伝搬と逆伝搬の計算
class Affine:
    def __init__(self, W, b):
        self.W = W
        self.b = b
        self.x = None
        self.dW = None
        self.db = None
        self.orignal_x_shape = None

    def forward(self, x, train_flg: bool = False):
        self.orignal_x_shape = x.shape
        x = x.reshape(x.shape[0], -1)
        self.x = x

        out = np.dot(self.x, self.W) + self.b

        return out

    def backward(self, dout):
        dx = np.dot(dout, self.W.T)
        self.dW = np.dot(self.x.T, dout)
        self.db = np.sum(dout, axis=0)

        dx = dx.reshape(*self.orignal_x_shape)
        return dx


# ソフトマックスと損失関数の組み合わせた順伝搬と逆伝搬の計算
class SoftmaxWithLoss:
    def __init__(self):
        self.t = None
        self.y = None
        self.loss = None

    def forward(self, x, t):
        self.t = t
        self.y = function.softmax(x)
        self.loss = function.cross_entropy_error_batch(self.y, self.t)

        return self.loss

    def backward(self, dout=1.0):
        batch_size = self.t.shape[0]
        if self.t.size == self.y.size:
            dx = (self.y - self.t) / batch_size
        # 正解ラベルがある場合
        else:
            dx = self.y.copy()
            dx[np.arange(batch_size), self.t] -= 1.0
            dx = dx / batch_size

        return dx


# Batch Normalization
# 目的は各層のアクティベーションの分布を適度な広がりを出す
# 学習をスムーズにするようにできる
class BatchNormalization:
    def __init__(self, gamma, beta, momentum=0.9, running_mean=None, running_var=None):
        self.gamma = gamma
        self.beta = beta
        self.momentum = momentum
        self.input_shape = None

        self.running_mean = running_mean
        self.running_var = running_var

        self.batch_size = None
        self.xc = None
        self.std = None
        self.dgamma = None
        self.dbeta = None

    def forward(self, x, train_flg: bool = False):
        self.input_shape = x.shape
        if x.ndim != 2:
            N, C, H, W = x.shape
            x = x.reshape(N, -1)

        out = self.__forward(x, train_flg)
        return out.reshape(*self.input_shape)

    def __forward(self, x, train_flg: bool):
        if self.running_mean is None:
            N, D = x.shape
            self.running_mean = np.zeros(D)
            self.running_var = np.zeros(D)

        if train_flg:
            # 1/mΣxi
            mu = x.mean(axis=0)
            # 1/mΣ(xi - ub)**2
            xc = x - mu
            var = np.mean(xc**2, axis=0)

            # xi-ub/√a**2 + e
            std = np.sqrt(var + 10e-7)
            xn = xc / std

            self.batch_size = x.shape[0]
            self.xc = xc
            self.xn = xn
            self.std = std
            self.running_mean = (
                self.momentum * self.running_mean + (1.0 - self.momentum) * mu
            )
            self.running_var = (
                self.momentum * self.running_var + (1.0 - self.momentum) * var
            )
        else:
            xc = x - self.running_mean
            xn = xc / ((np.sqrt(self.running_var + 10e-7)))

        out = self.gamma * xn + self.beta
        return out

    def backward(self, dout):
        if dout.ndim != 2:
            N, C, H, W = dout.shape
            dout = dout.reshape(N, -1)

        dx = self.__backward(dout)
        dx = dx.reshape(*self.input_shape)

        return dx

    def __backward(self, dout):
        dbeta = dout.sum(axis=0)
        dgamma = np.sum(self.xn * dout, axis=0)
        dxn = self.gamma * dout
        dxc = dxn / self.std
        dstd = -np.sum((dxn * self.xc) / (self.std * self.std), axis=0)
        dvar = 0.5 * dstd / self.std
        dxc += (2.0 / self.batch_size) * self.xc * dvar
        dmu = np.sum(dxc, axis=0)
        dx = dxc - dmu / self.batch_size

        self.dgamma = dgamma
        self.dbeta = dbeta

        return dx


# Dropoutのレイヤー
# 学習中に利用するニューロンをランダムで選択して学習効率を上げる
class Dropout:
    def __init__(self, dropout_ratio=0.5):
        self.dropout_ratio = dropout_ratio
        self.mask = None

    def forward(self, x, train_flg: bool):
        if train_flg:
            self.mask = np.random.rand(*x.shape) > self.dropout_ratio
            return x * self.mask
        else:
            return x * (1.0 - self.dropout_ratio)

    def backward(self, dout):
        return dout * self.mask


class Convolution:
    def __init__(self, W, b, stride=1, pad=0):
        self.W = W
        self.b = b
        self.stride = stride
        self.pad = pad

    def forward(self, x, train_flg: bool):
        FN, C, FH, FW = self.W.shape
        N, C, H, W = x.shape
        out_h: int = int(1 + (H + 2 * self.pad - FH) // self.stride)
        out_w: int = int(1 + (W + 2 * self.pad - FW) // self.stride)

        col = util.im2col(x, FH, FW, self.stride, self.pad)
        col_W = self.W.reshape(FN, -1).T

        out = np.dot(col, col_W) + self.b
        out = out.reshape(N, out_h, out_w, -1).transpose(0, 3, 1, 2)

        self.x = x
        self.col = col
        self.col_W = col_W

        return out

    def backward(self, dout):
        FN, C, FH, FW = self.W.shape
        dout = dout.transpose(0, 2, 3, 1).reshape(-1, FN)

        self.db = np.sum(dout, axis=0)
        self.dW = np.dot(self.col.T, dout)
        self.dW = self.dW.transpose(1, 0).reshape(FN, C, FH, FW)

        dcol = np.dot(dout, self.col_W.T)
        dx = util.col2im(dcol, self.x.shape, FH, FW, self.stride, self.pad)

        return dx


class Pooling:
    def __init__(self, pool_h, pool_w, stride=1, pad=0):
        self.pool_h = pool_h
        self.pool_w = pool_w
        self.stride = stride
        self.pad = pad

    def forward(self, x, train_flg: bool):
        N, C, H, W = x.shape

        out_h: int = int(1 + (H - self.pool_h) // self.stride)
        out_w: int = int(1 + (W - self.pool_w) // self.stride)

        col = util.im2col(x, self.pool_h, self.pool_w, self.stride, self.pad)
        col = col.reshape(-1, self.pool_h * self.pool_w)

        arg_max = np.argmax(col, axis=1)
        # プーリングした領域の最大値を取得した配列を作る
        out = np.max(col, axis=1)
        out = out.reshape(N, out_h, out_w, C).transpose(0, 3, 1, 2)

        self.x = x
        self.arg_max = arg_max

        return out

    def backward(self, dout):
        dout = dout.transpose(0, 2, 3, 1)

        pool_size = self.pool_h * self.pool_w
        dmax = np.zeros((dout.size, pool_size))
        dmax[np.arange(self.arg_max.size), self.arg_max.flatten()] = dout.flatten()
        dmax = dmax.reshape(dout.shape + (pool_size,))

        dcol = dmax.reshape(dmax.shape[0] * dmax.shape[1] * dmax.shape[2], -1)
        dx = util.col2im(
            dcol, self.x.shape, self.pool_h, self.pool_w, self.stride, self.pad
        )

        return dx
