#!/usr/bin/env python
# 7章 畳み込みニューラルネットワーク
# 上記の章を呼んだ内容から作成したテストコード

import numpy as np
import modules.common.util as util
import modules.neural_net.simple_conv_net as simple_conv_net


def test_np():
    # numpyのテスト

    # 4次元のデータを作成
    x: np.NDArray[np.float64] = np.random.rand(10, 1, 28, 28)
    print(x.shape)
    print(x.shape[0])
    N, C, H, W = x.shape
    print(f"N({N}),C({C}),H({H}),W({W})")

    # 4次元なのに3要素指定しているのでエラーとなる
    # N, C, H = x.shape
    # print(f'N({N}),C({C}),H({H}),W({W})')

    for i in range(x.shape[0]):
        print(x[i].shape)


def test_im2col():
    # im2colのテスト

    # 4次元のデータを作成
    img: np.NDArray[np.float64] = np.random.rand(1, 1, 4, 4)
    col = util.im2col(img, filter_h=2, filter_w=2, stride=1, pad=0)
    print(f"入力形状:{img.shape}")
    print(f"入力画像:\n{img}")
    print(f"出力画像:\n{col}")
    print(f"出力形状:{col.shape}")


def test_simple_conv_net():
    # convolution / pooling レイヤーを使った学習

    def __trainer(
        network,
        x_train,
        t_train,
        x_test,
        t_test,
        mini_batch_size: int = 100,
        evaluate_sample_num_per_epoch: int = 1000,
        lr: float = 0.001,
        epocs: int = 50,
    ):
        import modules.common.optmizer as optmizer

        # 最適化関数
        opt = optmizer.Adam(lr=lr)

        train_size: int = x_train.shape[0]
        iter_per_epoch = max(train_size / mini_batch_size, 1)
        max_iter: int = int(epocs * iter_per_epoch)

        train_acc_list = list()
        test_acc_list = list()

        # 試行回数
        for i in range(max_iter):
            # 学習するバッチを作成
            batch_mask = np.random.choice(train_size, mini_batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 勾配を求める
            grads = network.gradient(x_batch, t_batch)
            # 勾配を最適化
            opt.update(network.params, grads)

            # 認識精度を取得して記録
            if i % iter_per_epoch == 0:
                x_train_sample, t_train_sample = x_train, t_train
                x_test_sample, t_test_sample = x_test, t_test
                if 0 < evaluate_sample_num_per_epoch:
                    x_train_sample, t_train_sample = (
                        x_train[:evaluate_sample_num_per_epoch],
                        t_train[:evaluate_sample_num_per_epoch],
                    )

                    x_test_sample, t_test_sample = (
                        x_test[:evaluate_sample_num_per_epoch],
                        t_test[:evaluate_sample_num_per_epoch],
                    )

                train_acc = network.accracy(x_train_sample, t_train_sample)
                test_acc = network.accracy(x_test_sample, t_test_sample)
                train_acc_list.append(train_acc)
                test_acc_list.append(test_acc)

        return test_acc_list, train_acc_list

    try:
        import pathlib as path
        import os
        import modules.dataset.mnist as mnist

        # 機械学習する手書きの数字画像の訓練とテストデータをダウンロード
        # ダウンロード先のディレクトリを絶対パスで生成
        data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
        data_path = data_path.joinpath("data/test_ep03/")
        mnist.init_mnist(download_path=data_path)

        # ダウンロードする
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(flatten=False)

        # 学習ネットワーク構築
        net: simple_conv_net.SimpleConvNet = simple_conv_net.SimpleConvNet(
            input_dim=(1, 28, 28),
            conv_param={"filter_num": 30, "filter_size": 5, "pad": 0, "stride": 1},
            hidden_size=100,
            output_size=10,
            weight_init_std=0.01,
        )

        # 構築したネットワークに基づき学習訓練
        max_epcos: int = 20
        test_acc_list, train_acc_list = __trainer(
            network=net,
            x_train=x_train,
            t_train=t_train,
            x_test=x_test,
            t_test=t_test,
            mini_batch_size=100,
            evaluate_sample_num_per_epoch=1000,
            lr=0.001,
            epocs=max_epcos,
        )

        # モデルを保存
        model_file_path: path.Path = path.Path(
            os.path.dirname(os.path.abspath(__file__))
        )
        model_file_path = model_file_path.joinpath("data/test_ep07/params.pk1")
        net.save_params(file_name=model_file_path)

        # グラフの描画
        x = np.arange(max_epcos)

        import matplotlib.pyplot as plt

        plt.plot(x, train_acc_list, marker="o", label="train", markevery=2)
        plt.plot(x, test_acc_list, marker="s", label="test", markevery=2)
        plt.xlabel("epochs")
        plt.ylabel("accuracy")
        plt.ylim(0, 1.0)
        plt.legend(loc="lower right")
        plt.show()

    except Exception as identifier:
        print(identifier)
        assert 0


def test_cnn_visualize_filter():
    # 学習前の重みと学習後の重みをそれぞれ画像表示して比較することができる

    def __filter_show(filters, nx: int = 8, margin: int = 3, scale: int = 10):
        FN, C, FH, FW = filters.shape
        ny = int(np.ceil(FN / nx))

        import matplotlib.pyplot as plt

        fig: plt.Figure = plt.figure()
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.05, wspace=0.05)

        for i in range(FN):
            ax = fig.add_subplot(ny, nx, i + 1, xticks=[], yticks=[])
            ax.imshow(filters[i, 0], cmap=plt.cm.gray_r, interpolation="nearest")
        plt.show()

    network = simple_conv_net.SimpleConvNet()
    # 学習前の重みを表示
    __filter_show(network.params["W1"])

    import pathlib as path
    import os

    # 学習して作成したモデルをロード
    model_file_path: path.Path = path.Path(os.path.dirname(os.path.abspath(__file__)))
    model_file_path = model_file_path.joinpath("data/test_ep07/params.pk1")

    network.load_params(file_name=model_file_path)
    # 学習後の重みを表示
    __filter_show(network.params["W1"])
