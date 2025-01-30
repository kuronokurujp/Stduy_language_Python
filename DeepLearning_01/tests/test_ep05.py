#!/usr/bin/env python

# 5章 誤差逆伝播法
# 上記の章を呼んだ内容から作成したテストコード

import modules.common.layer as layer
import modules.neural_net.layer as net_layer
import modules.common.optmizer as optmizer


# 掛け算のレイヤ
class MulLayer:
    def __init__(self):
        self.x = None
        self.y = None

    # 順伝播
    def forward(self, x, y):
        self.x = x
        self.y = y
        return self.x * self.y

    # 逆伝播
    def backward(self, dout):
        # 要素を逆にして積算
        dx = self.y * dout
        dy = self.x * dout
        return dx, dy


# 足し算のレイヤ
class AddLayer:
    def __init__(self):
        pass

    # 順伝播
    def forward(self, x, y):
        return x + y

    # 逆伝播
    def backward(self, dout):
        # 変化しない
        dx = 1.0 * dout
        dy = 1.0 * dout
        return dx, dy


def test_mull_layer():
    # 掛け算の順伝播と逆伝播を試す

    mul_apple_layer = MulLayer()
    mul_tax_layer = MulLayer()
    print("")

    apple = 100
    apple_num = 2
    tax = 1.1
    apple_price = mul_apple_layer.forward(apple, apple_num)
    print(apple_price)
    total_price = mul_tax_layer.forward(apple_price, tax)
    print(total_price)

    dapple_price, dtax = mul_tax_layer.backward(1.0)
    print(dapple_price, dtax)

    dapple, dapple_num = mul_apple_layer.backward(dapple_price)
    print(dapple, dapple_num)


def test_add_layer():
    # 足し算の順伝播と逆伝播のテスト

    add_layer = AddLayer()
    print("")
    total = add_layer.forward(100, 50)
    print(total)

    dtotal, d = add_layer.backward(1)
    print(dtotal, d)


def test_add_mul_layer():
    # 足し算と掛け算の順伝播と逆伝播についてテスト

    apple = 100
    apple_num = 2
    tax = 1.1
    orange = 150
    orange_num = 3

    # レイヤ
    mul_apple_layer = MulLayer()
    mul_orange_layer = MulLayer()
    add_apple_orange_layer = AddLayer()
    mul_tax_layer = MulLayer()

    # 各レイヤの順伝搬での計算
    apple_price = mul_apple_layer.forward(apple, apple_num)
    orange_price = mul_orange_layer.forward(orange, orange_num)
    all_price = add_apple_orange_layer.forward(apple_price, orange_price)
    total_price = mul_tax_layer.forward(all_price, tax)

    print("")
    print(total_price)

    # 順伝搬後の逆伝搬での計算
    # 順伝搬で計算した変化値を求めている
    # なので順伝搬での計算要素を保存する必要がある
    dall_price, dtax = mul_tax_layer.backward(1.0)
    dapple_price, dorange_price = add_apple_orange_layer.backward(dall_price)
    dorage, dorange_num = mul_orange_layer.backward(dorange_price)
    dapple, dapple_num = mul_apple_layer.backward(dapple_price)

    print(dapple, dapple_num, dorage, dorange_num, dtax)


def test_layer_relu():
    # Reluの順伝播と逆伝播のテスト

    relu = layer.Relu()
    import numpy as np

    print("")

    x = np.array([[1.0, -0.5], [-2.0, 3.0]])
    o = relu.forward(x)
    print(o)

    dout = np.array([[3.0, -0.5], [-2.0, 3.0]])
    o = relu.backward(dout)
    print(o)


def test_check_gradient():
    # 勾配降下法と誤差逆伝播法との結果を比較
    # 実行完了には1日以上の時間が必要かもしれない

    import modules.dataset.mnist as mnist

    import pathlib as path
    import numpy as np
    import os

    try:
        # 機械学習する手書きの数字画像の訓練とテストデータをダウンロード
        # ダウンロード先のディレクトリを絶対パスで生成
        data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
        data_path = data_path.joinpath("data/test_ep03/")
        mnist.init_mnist(download_path=data_path)

        # ダウンロードする
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(
            normalize=True, one_hot_label=True
        )

        # ミニバッチを使ってニューラルネットワークの学習をする
        net = net_layer.TwoLayer(input_size=28 * 28, hidden_size=50, output_size=10)

        x_batch = x_train[:3]
        t_batch = t_train[:3]

        grads_numerical = net.numerical_gradient(x_batch, t_batch)
        grads_backprop = net.gradient(x_batch, t_batch)

        for key in grads_numerical.keys():
            diff = np.average(np.abs(grads_backprop[key] - grads_numerical[key]))
            print(f"{key}: {diff}")

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_twolayer_epoch():
    # エポックを使った2レイヤのニューラルネットワークの学習

    try:
        import modules.dataset.mnist as mnist

        import pathlib as path
        import numpy as np
        import os

        # 機械学習する手書きの数字画像の訓練とテストデータをダウンロード
        # ダウンロード先のディレクトリを絶対パスで生成
        data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
        data_path = data_path.joinpath("data/test_ep03/")
        mnist.init_mnist(download_path=data_path)

        # ダウンロードする
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)

        # 損失/認識の結果
        trans_loss_list = []
        train_acc_list = []
        test_acc_list = []

        train_size = x_train.shape[0]
        # バッチサイズ
        batch_size = 100
        # 訓練データ数とバッチサイズから訓練結果を受け取るカウント数
        iter_per_epoch = max(train_size / batch_size, 1)

        # 学習回数
        iters_num = 10000
        learning_rate = 0.1
        opt = optmizer.SGD(learning_rate)

        # ミニバッチを使ってニューラルネットワークの学習をする
        net: net_layer.TwoLayer = net_layer.TwoLayer(
            input_size=28 * 28, hidden_size=50, output_size=10
        )

        for i in range(iters_num):
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 勾配を求める
            grads = net.gradient(x_batch, t_batch)
            # 確率的勾配降下法で勾配を最適化
            opt.update(net.params, grads)

            # 損失値を出す
            loss = net.loss(x_batch, t_batch)
            # 損失値をリストに保存
            trans_loss_list.append(loss)

            # 学習結果をリストに保存
            if i % iter_per_epoch == 0:
                train_acc = net.accracy(x_train, t_train)
                test_acc = net.accracy(x_test, t_test)
                train_acc_list.append(train_acc)
                test_acc_list.append(test_acc)
                print(f"train acc, test acc | {str(train_acc)}, {str(test_acc)}")

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("epoch")
        plt.ylabel("accracy")
        x = range(len(train_acc_list))
        plt.plot(x, train_acc_list, label="train acc")
        plt.plot(x, test_acc_list, label="test acc", linestyle="--")
        plt.legend(loc="lower right")
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False
