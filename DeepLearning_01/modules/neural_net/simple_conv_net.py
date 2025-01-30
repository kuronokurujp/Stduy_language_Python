#!/usr/bin/env python
import modules.common.layer as common_layer
import modules.common.gradient as common_gradient
import pathlib as path
import numpy as np


# CNNの簡易ネット
class SimpleConvNet:
    def __init__(
        self,
        input_dim=(1, 28, 28),
        conv_param={"filter_num": 30, "filter_size": 5, "pad": 0, "stride": 1},
        hidden_size=100,
        output_size=10,
        weight_init_std=0.01,
    ):
        filter_num: int = conv_param["filter_num"]
        filter_size: int = conv_param["filter_size"]
        filter_pad: int = conv_param["pad"]
        filter_stride: int = conv_param["stride"]

        input_size: int = input_dim[1]
        conv_output_size: int = int(
            (input_size - filter_size + 2 * filter_pad) / filter_stride + 1
        )

        pool_output_size: int = int(
            filter_num * (conv_output_size / 2) * (conv_output_size / 2)
        )

        self.params = {}
        # 重みのパラメータとバイアスをランダムで生成
        # 2層のニューラルネットワークなので隠れ層は1つ
        # 隠れ層の重みとパラメータを作成
        self.params["W1"] = weight_init_std * np.random.randn(
            filter_num, input_dim[0], filter_size, filter_size
        )
        self.params["b1"] = np.zeros(filter_num)

        self.params["W2"] = weight_init_std * np.random.randn(
            pool_output_size, hidden_size
        )
        self.params["b2"] = np.zeros(hidden_size)

        # 出力層の重みとパラメータを作成
        self.params["W3"] = weight_init_std * np.random.randn(hidden_size, output_size)
        self.params["b3"] = np.zeros(output_size)

        # レイヤー生成
        self.layers = {}
        # 隠れ層の重みとバイアス
        self.layers["Conv1"] = common_layer.Convolution(
            self.params["W1"],
            self.params["b1"],
            conv_param["stride"],
            conv_param["pad"],
        )
        # 活性関数
        self.layers["Relu1"] = common_layer.Relu()

        # プーリング層
        self.layers["Pool"] = common_layer.Pooling(pool_h=2, pool_w=2, stride=2)

        self.layers["Affine1"] = common_layer.Affine(
            self.params["W2"], self.params["b2"]
        )
        self.layers["Relu2"] = common_layer.Relu()

        # 出力層の重みとバイアス
        self.layers["Affine2"] = common_layer.Affine(
            self.params["W3"], self.params["b3"]
        )

        # 隠れ層から受け取ったパラメータの活性関数と損失関数を出す出力層
        self.lastLayer = common_layer.SoftmaxWithLoss()

    def predict(self, x):
        # 各レイヤーの計算
        for l in self.layers.values():
            x = l.forward(x, False)

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
        grads["W1"] = common_gradient.numerical_gradient(loss_W, self.params["W1"])
        grads["b1"] = common_gradient.numerical_gradient(loss_W, self.params["b1"])
        grads["W2"] = common_gradient.numerical_gradient(loss_W, self.params["W2"])
        grads["b2"] = common_gradient.numerical_gradient(loss_W, self.params["b2"])
        grads["W3"] = common_gradient.numerical_gradient(loss_W, self.params["W3"])
        grads["b3"] = common_gradient.numerical_gradient(loss_W, self.params["b3"])

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
        grads["W1"] = self.layers["Conv1"].dW
        grads["b1"] = self.layers["Conv1"].db
        # 2層目の重みとバイアス
        grads["W2"] = self.layers["Affine1"].dW
        grads["b2"] = self.layers["Affine1"].db

        grads["W3"] = self.layers["Affine2"].dW
        grads["b3"] = self.layers["Affine2"].db

        return grads

    def save_params(self, file_name: path.Path):
        params = {}
        for key, val in self.params.items():
            params[key] = val

        import pickle

        # 親ディレクトリがない場合は作成
        if file_name.is_dir():
            file_name.mkdir(parents=True, exist_ok=True)
        else:
            file_name.parent.mkdir(parents=True, exist_ok=True)

        with open(file_name.as_posix(), "wb") as f:
            pickle.dump(params, f)

    def load_params(self, file_name: path.Path):
        import pickle

        with open(file_name.as_posix(), "rb") as f:
            params = pickle.load(f)

        for key, val in params.items():
            self.params[key] = val
