#!/usr/bin/env python
import numpy as np
import modules.common.gradient as gradient
import modules.common.function as function
import modules.common.layer as layer
from collections import OrderedDict


# ニューラルネットワークの学習レイヤー
# 入力と隠れ層と出力層のみ限定
class MultiLayer:
    def __init__(
        self,
        input_size: int,
        hidden_size_list: list[int],
        output_size: int,
        weight_init_std=0.1,
    ):
        weight_no = 0
        self.params = {}

        # 重みのパラメータとバイアスをランダムで生成
        # 2層のニューラルネットワークなので隠れ層は1つ
        # 隠れ層の重みとパラメータを作成

        scale: float = self.__get_weight_scale(weight_init_std, input_size)
        self.params[f"W{weight_no}"] = scale * np.random.randn(
            input_size, hidden_size_list[0]
        )
        self.params[f"b{weight_no}"] = np.zeros(hidden_size_list[0])
        weight_no += 1

        # 中間層の生成
        for i in range(0, len(hidden_size_list) - 1):
            now_size = hidden_size_list[i]
            next_size = hidden_size_list[i + 1]

            scale: float = self.__get_weight_scale(weight_init_std, now_size)

            self.params[f"W{weight_no}"] = scale * np.random.randn(now_size, next_size)
            self.params[f"b{weight_no}"] = np.zeros(next_size)
            weight_no += 1

        # 出力層の重みとパラメータを作成
        last_hidden_idx = len(hidden_size_list) - 1

        scale: float = self.__get_weight_scale(
            weight_init_std, hidden_size_list[last_hidden_idx]
        )
        self.params[f"W{weight_no}"] = scale * np.random.randn(
            hidden_size_list[last_hidden_idx], output_size
        )
        self.params[f"b{weight_no}"] = np.zeros(output_size)

        # レイヤー生成
        weight_no = 0
        self.layers = OrderedDict()
        # 隠れ層の重みとバイアス
        self.layers[f"Affine{weight_no}"] = layer.Affine(
            self.params[f"W{weight_no}"], self.params[f"b{weight_no}"]
        )
        # 活性関数
        self.layers[f"Acitivation{weight_no}"] = self.__get_activation_layer(
            weight_init_std
        )
        weight_no += 1

        # 中間層の生成
        for i in range(0, len(hidden_size_list) - 1):
            # 隠れ層の重みとバイアス
            self.layers[f"Affine{weight_no}"] = layer.Affine(
                self.params[f"W{weight_no}"], self.params[f"b{weight_no}"]
            )
            # 活性関数
            self.layers[f"Activation{weight_no}"] = self.__get_activation_layer(
                weight_init_std
            )
            weight_no += 1

        # 出力層の重みとバイアス
        self.layers[f"Affine{weight_no}"] = layer.Affine(
            self.params[f"W{weight_no}"], self.params[f"b{weight_no}"]
        )

        # 重み層の最大値
        self.weight_layer_max = weight_no + 1

        # 隠れ層から受け取ったパラメータの活性関数と損失関数を出す出力層
        self.lastLayer = layer.SoftmaxWithLoss()

    def predict(self, x):
        # 各レイヤーの計算
        for lay in self.layers.values():
            x = lay.forward(x)

        return x

    def loss(self, x, t):
        # 出力層の一つ手前の結果を受け取る
        y = self.predict(x)

        weight_decay = 0
        # 出力層の計算を損失値を返す
        return self.lastLayer.forward(y, t) + weight_decay

    def accracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)

        accracy = np.sum(y == t) / float(x.shape[0])
        return accracy

    def numerical_gradient(self, x, t):
        # 損失関数を使って重みとバイアスのパラメータを更新
        loss_W = lambda W: self.loss(x, t)
        grads = {}
        for i in range(self.weight_layer_max):
            grads[f"W{i}"] = gradient.numerical_gradient(loss_W, self.params[f"W{i}"])
            grads[f"b{i}"] = gradient.numerical_gradient(loss_W, self.params[f"b{i}"])

        return grads

    def gradient(self, x, t):
        # 順伝搬
        self.loss(x, t)

        # 逆伝搬
        dout = 1
        dout = self.lastLayer.backward(dout)
        layers = list(self.layers.values())
        layers.reverse()
        for l in layers:
            dout = l.backward(dout)

        grads = {}
        for layer_no in range(self.weight_layer_max):
            grads[f"W{layer_no}"] = self.layers[f"Affine{layer_no}"].dW
            grads[f"b{layer_no}"] = self.layers[f"Affine{layer_no}"].db

        return grads

    def __get_activation_layer(self, type):
        if isinstance(type, str):
            if type == "sigmoid":
                # Tanh関数を利用
                # return layer.Sigmoid()
                return layer.Tanh()
            elif type == "relu":
                return layer.Relu()
        else:
            return layer.Sigmoid()

    def __get_weight_scale(self, type, node_num):
        if isinstance(type, str):
            if type == "sigmoid":
                n: float = 1.0 / float(node_num)
                return np.sqrt(n)
            elif type == "relu":
                n: float = 2.0 / float(node_num)
                return np.sqrt(n)
        else:
            return type


# ニューラルネットワークの学習レイヤー
# 入力と隠れ層と出力層のみ限定
class TwoLayer:
    def __init__(self, input_size, hidden_size, output_size, weight_init_std=0.01):
        self.params = {}
        # 重みのパラメータとバイアスをランダムで生成
        # 2層のニューラルネットワークなので隠れ層は1つ
        # 隠れ層の重みとパラメータを作成
        self.params["W1"] = weight_init_std * np.random.randn(input_size, hidden_size)
        self.params["b1"] = np.zeros(hidden_size)

        # 出力層の重みとパラメータを作成
        self.params["W2"] = weight_init_std * np.random.randn(hidden_size, output_size)
        self.params["b2"] = np.zeros(output_size)

        # レイヤー生成
        self.layers = OrderedDict()
        # 隠れ層の重みとバイアス
        self.layers["Affine1"] = layer.Affine(self.params["W1"], self.params["b1"])
        # 活性関数
        self.layers["Relu1"] = layer.Relu()
        # 出力層の重みとバイアス
        self.layers["Affine2"] = layer.Affine(self.params["W2"], self.params["b2"])

        # 隠れ層から受け取ったパラメータの活性関数と損失関数を出す出力層
        self.lastLayer = layer.SoftmaxWithLoss()

    def predict(self, x):
        # 各レイヤーの計算
        for l in self.layers.values():
            x = l.forward(x)

        return x

    def loss(self, x, t):
        # 出力層の一つ手前の結果を受け取る
        y = self.predict(x)
        # 出力層の計算を損失値を返す
        return self.lastLayer.forward(y, t)

    def accracy(self, x, t):
        y = self.predict(x)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)

        accracy = np.sum(y == t) / float(x.shape[0])
        return accracy

    def numerical_gradient(self, x, t):
        # 損失関数を使って重みとバイアスのパラメータを更新
        loss_W = lambda W: self.loss(x, t)
        grads = {}
        grads["W1"] = gradient.numerical_gradient(loss_W, self.params["W1"])
        grads["b1"] = gradient.numerical_gradient(loss_W, self.params["b1"])
        grads["W2"] = gradient.numerical_gradient(loss_W, self.params["W2"])
        grads["b2"] = gradient.numerical_gradient(loss_W, self.params["b2"])

        return grads

    def gradient(self, x, t):
        # 順伝搬
        self.loss(x, t)

        # 逆伝搬
        dout = 1
        dout = self.lastLayer.backward(dout)
        layers = list(self.layers.values())
        layers.reverse()
        for l in layers:
            dout = l.backward(dout)

        grads = {}
        # 1層目の重みとバイアス
        grads["W1"] = self.layers["Affine1"].dW
        grads["b1"] = self.layers["Affine1"].db
        # 2層目の重みとバイアス
        grads["W2"] = self.layers["Affine2"].dW
        grads["b2"] = self.layers["Affine2"].db

        return grads
