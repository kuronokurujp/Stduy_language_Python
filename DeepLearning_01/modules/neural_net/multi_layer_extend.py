#!/usr/bin/env python
import numpy as np
import modules.common.gradient as gradient
import modules.common.function as function
import modules.common.layer as layer
from collections import OrderedDict


# ニューラルネットワークの学習レイヤー(拡張版)
# 入力と隠れ層と出力層のみ限定
class Layer:
    def __init__(
        self,
        input_size: int,
        hidden_size_list: list[int],
        output_size: int,
        weight_init_std=0.1,
        weight_decay=0.0,
        use_batchnorm: bool = False,
        use_dropout: bool = False,
        dropout_ration: float = 0.5,
    ):
        weight_no = 0
        self.params = {}
        self.weight_decay = weight_decay
        self.use_batchnorm = use_batchnorm
        self.use_dropout = use_dropout
        self.dropout_ration = dropout_ration

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
        self.layers = {}
        # 隠れ層の重みとバイアス
        self.layers[f"Affine{weight_no}"] = layer.Affine(
            self.params[f"W{weight_no}"], self.params[f"b{weight_no}"]
        )
        if self.use_batchnorm:
            self.__create_batcn_norm_layer(
                self.layers, self.params, weight_no, hidden_size_list[0]
            )
        # 活性関数
        self.layers[f"Acitivation{weight_no}"] = self.__get_activation_layer(
            weight_init_std
        )
        # Dropoutをするかどうか
        if self.use_dropout:
            self.layers[f"Dropout{weight_no}"] = layer.Dropout(
                dropout_ratio=self.dropout_ration
            )

        weight_no += 1

        # 中間層の生成
        for i in range(0, len(hidden_size_list) - 1):
            # 隠れ層の重みとバイアス
            self.layers[f"Affine{weight_no}"] = layer.Affine(
                self.params[f"W{weight_no}"], self.params[f"b{weight_no}"]
            )

            if self.use_batchnorm:
                self.__create_batcn_norm_layer(
                    self.layers, self.params, weight_no, hidden_size_list[i + 1]
                )

            # 活性関数
            self.layers[f"Activation{weight_no}"] = self.__get_activation_layer(
                weight_init_std
            )
            # Dropoutをするかどうか
            if self.use_dropout:
                self.layers[f"Dropout{weight_no}"] = layer.Dropout(
                    dropout_ratio=self.dropout_ration
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

    def predict(self, x, train_flg: bool = False):
        # 各レイヤーの計算
        for lay in self.layers.values():
            x = lay.forward(x, train_flg=train_flg)

        return x

    def loss(self, x, t, train_flg: bool = False):
        # 出力層の一つ手前の結果を受け取る
        y = self.predict(x, train_flg=train_flg)

        add_weight_decay = 0
        for i in range(0, self.weight_layer_max):
            W = self.params[f"W{i}"]
            add_weight_decay += 0.5 * self.weight_decay * np.sum(W**2)

        # 出力層の計算を損失値を返す
        return self.lastLayer.forward(y, t) + add_weight_decay

    def accracy(self, x, t):
        y = self.predict(x, train_flg=False)
        y = np.argmax(y, axis=1)
        if t.ndim != 1:
            t = np.argmax(t, axis=1)

        accracy = np.sum(y == t) / float(x.shape[0])
        return accracy

    def numerical_gradient(self, x, t):
        # 損失関数を使って重みとバイアスのパラメータを更新
        loss_W = lambda W: self.loss(x, t, train_flg=True)
        grads = {}
        for i in range(self.weight_layer_max):
            grads[f"W{i}"] = gradient.numerical_gradient(loss_W, self.params[f"W{i}"])
            grads[f"b{i}"] = gradient.numerical_gradient(loss_W, self.params[f"b{i}"])

            if self.use_batchnorm and i < (self.weight_layer_max - 1):
                grads[f"gamma{i}"] = gradient.numerical_gradient(
                    loss_W, self.params[f"gamma{i}"]
                )
                grads[f"beta{i}"] = gradient.numerical_gradient(
                    loss_W, self.params[f"beta{i}"]
                )

        return grads

    def gradient(self, x, t):
        # 順伝搬
        self.loss(x, t, train_flg=True)

        # 逆伝搬
        dout = 1
        dout = self.lastLayer.backward(dout)
        layers = list(self.layers.values())
        layers.reverse()
        for lay in layers:
            dout = lay.backward(dout)

        grads = {}
        for layer_no in range(self.weight_layer_max):
            grads[f"W{layer_no}"] = (
                self.layers[f"Affine{layer_no}"].dW
                + self.weight_decay * self.layers[f"Affine{layer_no}"].W
            )
            grads[f"b{layer_no}"] = self.layers[f"Affine{layer_no}"].db

            if self.use_batchnorm and layer_no < (self.weight_layer_max - 1):
                grads[f"gamma{layer_no}"] = self.layers[f"BatcnNorm{layer_no}"].dgamma
                grads[f"beta{layer_no}"] = self.layers[f"BatcnNorm{layer_no}"].dbeta

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

    # BatcnNormのレイヤーを作成
    def __create_batcn_norm_layer(self, layers, params, weight_no, node_size):
        params[f"gamma{weight_no}"] = np.ones(node_size)
        params[f"beta{weight_no}"] = np.zeros(node_size)
        layers[f"BatcnNorm{weight_no}"] = layer.BatchNormalization(
            params[f"gamma{weight_no}"], params[f"beta{weight_no}"]
        )
