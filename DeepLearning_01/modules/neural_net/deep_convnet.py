#!/usr/bin/env python
import modules.common.layer as common_layer
import pathlib as path
import numpy as np


class DeepConvNet:
    def __init__(
        self,
        input_dim=(1, 28, 28),
        conv_param_1={"filter_num": 16, "filter_size": 3, "pad": 1, "stride": 1},
        conv_param_2={"filter_num": 16, "filter_size": 3, "pad": 1, "stride": 1},
        conv_param_3={"filter_num": 32, "filter_size": 3, "pad": 1, "stride": 1},
        conv_param_4={"filter_num": 32, "filter_size": 3, "pad": 2, "stride": 1},
        conv_param_5={"filter_num": 64, "filter_size": 3, "pad": 1, "stride": 1},
        conv_param_6={"filter_num": 64, "filter_size": 3, "pad": 1, "stride": 1},
        hidden_size=50,
        output_size=10,
    ):
        # 浮動小数点を全部半精度にしてみる

        self.params = {}
        pre_node_nums = np.array(
            [
                1 * 3 * 3,
                16 * 3 * 3,
                16 * 3 * 3,
                32 * 3 * 3,
                32 * 3 * 3,
                64 * 3 * 3,
                64 * 4 * 4,
                hidden_size,
            ]
        )

        # 「Heの初期値」を作るガウス分布の値を作成
        weight_scale_list = np.sqrt(2.0 / pre_node_nums)
        pre_channel_num: int = input_dim[0]

        param_no: int = 1
        for i, conv_param in enumerate(
            [
                conv_param_1,
                conv_param_2,
                conv_param_3,
                conv_param_4,
                conv_param_5,
                conv_param_6,
            ]
        ):
            filter_num: int = conv_param["filter_num"]
            filter_size: int = conv_param["filter_size"]

            self.params[f"W{param_no}"] = weight_scale_list[i] * np.random.randn(
                filter_num, pre_channel_num, filter_size, filter_size
            ).astype(np.float16)
            self.params[f"b{param_no}"] = np.zeros(filter_num).astype(np.float16)

            pre_channel_num = filter_num
            param_no = param_no + 1

        self.params[f"W{param_no}"] = weight_scale_list[param_no - 1] * np.random.randn(
            64 * 4 * 4, hidden_size
        ).astype(np.float16)
        self.params[f"b{param_no}"] = np.zeros(hidden_size).astype(np.float16)
        param_no = param_no + 1

        self.params[f"W{param_no}"] = weight_scale_list[param_no - 1] * np.random.randn(
            hidden_size, output_size
        ).astype(np.float16)
        self.params[f"b{param_no}"] = np.zeros(output_size).astype(np.float16)
        param_no = param_no + 1

        # レイヤー生成
        self.layers = []
        self.layers.append(
            common_layer.Convolution(
                self.params["W1"],
                self.params["b1"],
                conv_param_1["stride"],
                conv_param_1["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())

        self.layers.append(
            common_layer.Convolution(
                self.params["W2"],
                self.params["b2"],
                conv_param_2["stride"],
                conv_param_2["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())
        self.layers.append(common_layer.Pooling(pool_h=2, pool_w=2, stride=2))

        self.layers.append(
            common_layer.Convolution(
                self.params["W3"],
                self.params["b3"],
                conv_param_3["stride"],
                conv_param_3["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())

        self.layers.append(
            common_layer.Convolution(
                self.params["W4"],
                self.params["b4"],
                conv_param_4["stride"],
                conv_param_4["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())
        self.layers.append(common_layer.Pooling(pool_h=2, pool_w=2, stride=2))

        self.layers.append(
            common_layer.Convolution(
                self.params["W5"],
                self.params["b5"],
                conv_param_5["stride"],
                conv_param_5["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())

        self.layers.append(
            common_layer.Convolution(
                self.params["W6"],
                self.params["b6"],
                conv_param_6["stride"],
                conv_param_6["pad"],
            )
        )
        # 活性関数
        self.layers.append(common_layer.Relu())
        self.layers.append(common_layer.Pooling(pool_h=2, pool_w=2, stride=2))

        self.layers.append(
            common_layer.Affine(
                self.params["W7"],
                self.params["b7"],
            )
        )
        self.layers.append(common_layer.Relu())
        self.layers.append(common_layer.Dropout(0.5))

        self.layers.append(
            common_layer.Affine(
                self.params["W8"],
                self.params["b8"],
            )
        )
        self.layers.append(common_layer.Dropout(0.5))

        # 隠れ層から受け取ったパラメータの活性関数と損失関数を出す出力層
        self.last_layer = common_layer.SoftmaxWithLoss()

    def predict(self, x, train_flg: bool = False):
        # 各レイヤーの計算
        for proc_layer in self.layers:
            x = proc_layer.forward(x, train_flg)

        return x

    def loss(self, x, t):
        # 出力層の一つ手前の結果を受け取る
        y = self.predict(x, train_flg=True)
        # 出力層の計算を損失値を返す
        return self.last_layer.forward(y, t)

    def accracy(self, x, t, batch_size: int = 100):
        if t.ndim != 1:
            t = np.argmax(t, axis=1)

        acc: float = 0.0
        for i in range(int(x.shape[0] / batch_size)):
            tx = x[i * batch_size : (i + 1) * batch_size]
            tt = t[i * batch_size : (i + 1) * batch_size]
            y = self.predict(tx, train_flg=False)
            y = np.argmax(y, axis=1)
            acc += np.sum(y == tt)

        return acc / x.shape[0]

    def gradient(self, x, t):
        # 順伝搬
        self.loss(x, t)

        # 逆伝搬
        dout = 1
        dout = self.last_layer.backward(dout)

        layers = self.layers.copy()
        layers.reverse()
        for proc_layer in layers:
            dout = proc_layer.backward(dout)

        grads = {}
        # 重みとバイアス
        for i, layer_idx in enumerate((0, 2, 5, 7, 10, 12, 15, 18)):
            param_no: int = i + 1
            grads[f"W{param_no}"] = self.layers[layer_idx].dW
            grads[f"b{param_no}"] = self.layers[layer_idx].db

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
