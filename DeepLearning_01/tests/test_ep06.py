#!/usr/bin/env python

# 6章 学習に関するテクニック
# 上記の章を呼んだ内容から作成したテストコード

import numpy as np
import modules.common.util as util
import modules.common.gradient as gradient
import modules.common.optmizer as optmizer
import modules.neural_net.layer as net_layer
import modules.neural_net.multi_layer_extend as multi_layer_net_extend


def test_3d_show():
    # 3D描画テスト

    x0 = np.arange(-10, 10, 0.25)
    x1 = np.arange(-10, 10, 0.25)
    X, Y = np.meshgrid(x0, x1)
    Z = ((X**2) / 20) + (Y**2)

    import matplotlib.pylab as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap="viridis")
    fig.colorbar(surf, shrink=0.5, aspect=5)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_label("3D Surface Plot")
    # Z軸の表示を右側から左側に見えるようにしている
    ax.view_init(elev=30, azim=45)
    # XY軸を反転させてXYともに原点から数値が増える表示にしている
    ax.invert_xaxis()
    ax.invert_yaxis()
    plt.show()


def test_contour_plot():
    # (xの2乗) / 20 + (yの2乗)の式を等高線でグラフ表示

    x = np.arange(-10.0, 10.0, 0.01)
    y = np.arange(-10.0, 10.0, 0.01)
    X, Y = np.meshgrid(x, y)
    Z = (X**2) / 20.0 + (Y**2)
    # 等高線の傾斜に制限をすることでグラフを表示を調整
    # 傾斜が0から200などの差が大きいとグラフに表示する傾斜パターンが多く
    # グラフ内に等高線がうまく納まらない
    mask = Z > 7
    Z[mask] = 0

    import matplotlib.pylab as plt

    plt.contour(X, Y, Z)
    plt.xlim(-10, 10)
    plt.ylim(-10, 10)
    plt.show()


def test_sgd_gradient_plot():
    # 偏微分から勾配を計算して2D上で表示

    x0 = np.arange(-2, 2.5, 0.25)
    print(f"x0={x0}")
    x1 = np.arange(-2, 2.5, 0.25)
    print(f"x1={x1}")
    # x0/x1の各軸行列を作成
    X, Y = np.meshgrid(x0, x1)
    print(f"X={X}")
    print(f"Y={Y}")

    # 各軸は行列になっているので一次元に変換
    X = X.flatten()
    Y = Y.flatten()
    print(f"X.flatten()={X}")
    print(f"Y.flatten()={Y}")

    def function_2(x):
        # XYの計算をする
        return (x[0] ** 2) / 20.0 + x[1] ** 2

    # XY行列を作成
    n = np.array([X, Y])
    # 転置してXYペアの形にして計算して勾配値を作る
    grad = gradient.numerical_gradient_2d(function_2, n.T)
    # XYペアの配列をgrad[0]をX配列,grad[1]をY配列の2要素の配列にする
    grad = grad.T
    print(f"grad={grad}")

    import matplotlib.pylab as plt

    plt.figure()
    # 勾配をベクトル表示させて勾配状態を視覚化
    plt.quiver(X, Y, -grad[0], -grad[1], angles="xy", color="#666666")
    plt.xlim([-2, 2])
    plt.ylim([-2, 2])
    plt.xlabel("x0")
    plt.ylabel("x1")
    plt.grid()
    plt.draw()
    plt.show()


def test_optimzer_contour_plot():
    # 各最適化の計算過程をグラフで表示

    init_pos = (-7.0, 2.0)
    opt_dict = {}
    # 確率的勾配降下法
    opt_dict["sgd"] = optmizer.SGD(lr=0.95)
    # モーメンタム
    # 学習率が高い(0.95とか)だと0に収束しない
    opt_dict["mom"] = optmizer.Momentum(lr=0.1)
    # AddGrad
    opt_dict["add_grad"] = optmizer.AdaGrad(lr=1.5)
    # Adam
    opt_dict["adam"] = optmizer.Adam(lr=0.3)

    import matplotlib.pylab as plt

    # グラフのプロットインデックス
    # 1初めなので注意
    sub_plot_idx = 1
    for opt_key, opt_obj in opt_dict.items():
        # 最適化の計算過程をxyリストに設定してグラフ表示させる
        x_history = []
        y_history = []
        params = {}
        params["x"] = init_pos[0]
        params["y"] = init_pos[1]
        for i in range(30):
            x_history.append(params["x"])
            y_history.append(params["y"])

            grads = {}
            # 微分計算
            grads["x"] = params["x"] / 10
            grads["y"] = 2 * params["y"]
            opt_obj.update(params=params, grads=grads)

        x = np.arange(-10.0, 10.0, 0.01)
        y = np.arange(-10.0, 10.0, 0.01)
        X, Y = np.meshgrid(x, y)
        Z = (X**2) / 20.0 + (Y**2)
        # 等高線の傾斜に制限をすることでグラフを表示を調整
        mask = Z > 7
        Z[mask] = 0

        # 最適化関数の計算過程のグラフを個々で作成
        plt.subplot(2, 2, sub_plot_idx)
        sub_plot_idx += 1

        plt.contour(X, Y, Z)
        plt.plot(x_history, y_history, "o-", color="red")

        plt.xlim(-10, 10)
        plt.ylim(-10, 10)
        plt.plot(0, 0, "+")
        plt.title(opt_key)
        plt.xlabel("x")
        plt.ylabel("y")

    plt.show()


def test_optmizer_by_mnist():
    # 各最適化関数を使った学習結果をグラフで表示

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
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)

        # 実行する最適化関数一覧
        opt_dict = {}
        # 確率的勾配降下法
        opt_dict["sgd"] = optmizer.SGD(lr=0.01)
        # モーメンタム
        # 学習率が高い(0.95とか)だと0に収束しない
        opt_dict["mom"] = optmizer.Momentum(lr=0.01)
        # AddGrad
        opt_dict["add_grad"] = optmizer.AdaGrad(lr=0.01)
        # Adam
        opt_dict["adam"] = optmizer.Adam(lr=0.001)

        network_dict: dict[str, net_layer.MultiLayer] = {}
        iters_num = 2000
        train_size = x_train.shape[0]
        batch_size = 128
        trans_loss_dict: dict[str, list] = {}

        for k in opt_dict.keys():
            # 活性関数はReluを使っている
            network_dict[k] = net_layer.MultiLayer(
                input_size=784,
                hidden_size_list=[100, 100, 100, 100],
                output_size=10,
                weight_init_std=0.1,
            )
            trans_loss_dict[k] = list()

        # 試行回数
        for i in range(iters_num):
            # 学習するバッチを作成
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 学習
            for key, network in network_dict.items():
                # 勾配を求める
                grads = network.gradient(x_batch, t_batch)
                # 勾配を最適化
                opt_dict[key].update(network.params, grads)

                # 損失値の経過を保存
                loss = network.loss(x_batch, t_batch)
                trans_loss_dict[key].append(loss)

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("iter")
        plt.ylabel("lost")

        def smooth_curve(x):
            window_len = 11
            s = np.r_[x[window_len - 1 : 0 : -1], x, x[-1:-window_len:-1]]
            w = np.kaiser(window_len, 2)
            y = np.convolve(w / w.sum(), s, mode="valid")
            return y[5 : len(y) - 5]

        #  各最適化の損失値の偏移を表示
        x = np.arange(iters_num)
        for k, v in trans_loss_dict.items():
            plt.plot(x, smooth_curve(v), label=k)

        plt.legend(loc="lower right")
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_weight_init_activation_histogram():
    # 重みの初期値の設定パターンを変えた結果をヒストグラムで表示

    # 入力データ作成
    input_data: np.NDArray[np.float64] = np.random.randn(1000, 100)
    # 隠れ層のデータ
    # 隠れ層の数
    hidden_layer_size: int = 5
    # 隠れ層のニューロンの数
    hidden_node_num: int = 100
    # 各隠れ層の活性関数の結果
    activaons: dict = dict()

    import modules.common.function as function

    activation_funcs: dict[str, dict] = dict()
    activation_funcs["sig"] = function.sigmoid
    activation_funcs["relu"] = function.relu
    activation_funcs["tanh"] = function.tanh

    for name, func in activation_funcs.items():
        activaons[name] = dict()

    #  最初は入力値を計算
    x = input_data
    for i in range(hidden_layer_size):
        # 各活性関数の計算結果を取得
        for name, activation_func in activation_funcs.items():
            if i != 0:
                x = activaons[name][i - 1]

            # 重みをガウス分布で生成
            if name == "relu":
                n = 2.0 / float(hidden_node_num)
                w = np.random.randn(hidden_node_num, hidden_node_num) * np.sqrt(n)
            else:
                # Xavier Glorotの論文だとガウス分布にノード数のルート値を割ると重みにばらつきを持たせることができる
                n = 1.0 / float(hidden_node_num)
                w = np.random.randn(hidden_node_num, hidden_node_num) * np.sqrt(n)

            # パラメータと重みを計算
            a = np.dot(x, w)

            # 活性関数に渡してニューロンの信号出力
            z = activation_func(a)

            # 信号出力を保存
            activaons[name][i] = z

    # 活性関数の結果をヒストグラムで表示
    import matplotlib.pyplot as plt

    # 各活性関数と各隠れ層の信号出力をプロット
    plot_idx = 1
    for name, a_dict in activaons.items():
        for idx, a in a_dict.items():
            ax = plt.subplot(len(activaons), len(a_dict), plot_idx)
            plt.title(f"{name}:{idx+1}-layer")
            # yticksをクリア
            if i != 0:
                plt.yticks([], [])
            # サブプロットの値の単位を共通
            ax.set_ylim(0, 7000)

            # ヒストグラムをプロット
            plt.hist(a.flatten(), 30, range=(0, 1))
            plot_idx += 1

    plt.tight_layout()
    plt.show()


def test_weight_test_by_mnist():
    # 重みの初期値を活性関数によって変えて学習した比較結果を表示
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
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)

        network_dict: dict[str, net_layer.MultiLayer] = {}
        iters_num = 2000
        train_size = x_train.shape[0]
        batch_size = 128
        trans_loss_dict: dict[str, list] = {}

        # 実行する重み一覧
        weigth_dict = {"std=0.01": 0.01, "Xavier": "sigmoid", "He": "relu"}
        for key, type in weigth_dict.items():
            network_dict[key] = net_layer.MultiLayer(
                input_size=784,
                hidden_size_list=[100, 100, 100, 100],
                output_size=10,
                weight_init_std=type,
            )
            trans_loss_dict[key] = list()

        # 最適化関数
        # コメント外して最適化関数を変えて異なる結果を試せる
        # opt: optmizer.Adam = optmizer.Adam(lr=0.01)
        # opt = optmizer.Momentum()
        opt = optmizer.SGD(lr=0.01)
        # 試行回数
        for i in range(iters_num):
            # 学習するバッチを作成
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 学習
            for key, network in network_dict.items():
                # 勾配を求める
                grads = network.gradient(x_batch, t_batch)
                # 勾配を最適化
                opt.update(network.params, grads)

                # 損失値の経過を保存
                loss = network.loss(x_batch, t_batch)
                trans_loss_dict[key].append(loss)

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("iter")
        plt.ylabel("lost")

        def smooth_curve(x):
            window_len = 11
            s = np.r_[x[window_len - 1 : 0 : -1], x, x[-1:-window_len:-1]]
            w = np.kaiser(window_len, 2)
            y = np.convolve(w / w.sum(), s, mode="valid")
            return y[5 : len(y) - 5]

        #  各最適化の損失値の偏移を表示
        markers = {"std=0.01": "o", "Xavier": "s", "He": "D"}
        x = np.arange(iters_num)
        for k, v in trans_loss_dict.items():
            plt.plot(x, smooth_curve(v), marker=markers[k], markevery=100, label=k)

        plt.legend(loc="lower right")
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_batch_norm():
    # Batch Normalizationアルゴリズムのレイヤーを使った学習結果を表示

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
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)
        # 学習データを削減
        x_train = x_train[:1000]
        t_train = t_train[:1000]

        max_epochs = 20
        train_size = x_train.shape[0]
        batch_size = 100

        # 実行する重み一覧
        bn_network = multi_layer_net_extend.Layer(
            input_size=28 * 28,
            hidden_size_list=[100, 100, 100, 100],
            output_size=10,
            weight_init_std=0.1,
            use_batchnorm=True,
        )
        network = multi_layer_net_extend.Layer(
            input_size=28 * 28,
            hidden_size_list=[100, 100, 100, 100],
            output_size=10,
            weight_init_std=0.1,
            use_batchnorm=False,
        )

        # 最適化関数
        opt = optmizer.SGD(lr=0.01)

        iter_per_epoch = max(train_size / batch_size, 1)
        epoch_cnt = 0

        train_acc_list = []
        bn_train_acc_list = []

        # 試行回数
        for i in range(1000000000):
            # 学習するバッチを作成
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 学習
            for _network in (bn_network, network):
                # 勾配を求める
                grads = _network.gradient(x_batch, t_batch)
                # 勾配を最適化
                opt.update(_network.params, grads)

            if i % iter_per_epoch == 0:
                train_acc = network.accracy(x_train, t_train)
                bn_train_acc = bn_network.accracy(x_train, t_train)
                train_acc_list.append(train_acc)
                bn_train_acc_list.append(bn_train_acc)

                print(f"epoch:{epoch_cnt} | {bn_train_acc}")
                epoch_cnt += 1

                if max_epochs <= epoch_cnt:
                    break

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("epoch")
        plt.ylabel("tran_acc")

        x = np.arange(len(train_acc_list))
        x = np.arange(len(bn_train_acc_list))
        plt.plot(x, train_acc_list, label="Norm", markevery=2)
        plt.plot(x, bn_train_acc_list, linestyle="--", label="Batch Norm", markevery=2)

        plt.legend(loc="lower right")
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_overfit_weigth_decay():
    # Batch Normalization / Dropoutを加えた学習結果を表示

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
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)
        # 学習データを削減
        x_train = x_train[:300]
        t_train = t_train[:300]

        max_epochs = 300
        train_size = x_train.shape[0]
        batch_size = 100

        network: multi_layer_net_extend.Layer = multi_layer_net_extend.Layer(
            input_size=28*28,
            hidden_size_list=[100, 100, 100, 100, 100, 100, 100],
            output_size=10,
            weight_init_std=0.1,
            weight_decay=0.1,
            use_batchnorm=True,
            use_dropout=True,
            dropout_ration=0.2,
        )

        # 最適化関数
        opt = optmizer.SGD(lr=0.01)

        iter_per_epoch = max(train_size / batch_size, 1)
        epoch_cnt = 0

        # 学習した後の認識値のリスト
        train_acc_list = []
        test_acc_list = []

        # 試行回数
        for i in range(1000000000):
            # 学習するバッチを作成
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            # 学習処理をする

            # 勾配を求める
            grads = network.gradient(x_batch, t_batch)
            # 勾配を最適化
            opt.update(network.params, grads)

            if i % iter_per_epoch == 0:
                # 訓練データの認識精度
                bn_test_acc = network.accracy(x_test, t_test)
                # テストデータの認識精度
                bn_train_acc = network.accracy(x_train, t_train)

                # それぞれの認識精度をリストに追加して精度変化を把握
                test_acc_list.append(bn_test_acc)
                train_acc_list.append(bn_train_acc)

                epoch_cnt += 1
                if max_epochs <= epoch_cnt:
                    break

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("epoch")
        plt.ylabel("acc")

        x = np.arange(len(train_acc_list))
        plt.plot(x, test_acc_list, label="Test", markevery=2)
        plt.plot(x, train_acc_list, linestyle="--", label="Train", markevery=2)

        plt.legend(loc="lower right")
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_hyper_param_validation():
    # ハイパーパラメータの検証した比較図

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
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(normalize=True)
        # 学習データを削減
        x_train = x_train[:500]
        t_train = t_train[:500]

        # 訓練データ数から検証データ数と訓練データ数を作り各データを作成する
        # 以下だと訓練データ数の20%(0.20)が検証データ/80%が訓練データ
        validation_rate: float = 0.20
        validation_num: int = int(x_train.shape[0] * validation_rate)

        # 訓練と教師データをシャッフル
        x_train, t_train = util.shuffle_dataset(x_train, t_train)
        # 検証データ作成
        x_val = x_train[:validation_num]
        t_val = t_train[:validation_num]
        # 訓練データ作成
        x_train = x_train[validation_num:]
        t_train = t_train[validation_num:]

        # 学習訓練
        def __train(lr, weight_decay, epocs=50):
            bn_network = multi_layer_net_extend.Layer(
                input_size=784,
                hidden_size_list=[100, 100, 100, 100, 100, 100, 100],
                output_size=10,
                weight_init_std="relu",
                weight_decay=weight_decay,
                use_batchnorm=True,
                use_dropout=True,
                dropout_ration=0.2,
            )

            # 最適化関数
            opt = optmizer.Adam(lr=lr)

            train_size: int = x_train.shape[0]
            batch_size: int = 100
            iter_per_epoch = max(train_size / batch_size, 1)
            max_iter: int = int(epocs * iter_per_epoch)

            train_acc_list = list()
            test_acc_list = list()

            # 試行回数
            for i in range(max_iter):
                # 学習するバッチを作成
                batch_mask = np.random.choice(train_size, batch_size)
                x_batch = x_train[batch_mask]
                t_batch = t_train[batch_mask]

                _network = bn_network
                # 勾配を求める
                grads = _network.gradient(x_batch, t_batch)
                # 勾配を最適化
                opt.update(_network.params, grads)

                # 認識精度を取得して記録
                if i % iter_per_epoch == 0:
                    train_acc = _network.accracy(x_train, t_train)
                    test_acc = _network.accracy(x_val, t_val)
                    train_acc_list.append(train_acc)
                    test_acc_list.append(test_acc)

            return test_acc_list, train_acc_list

        optimization_trial: int = 100
        result_val = {}
        result_trans = {}
        for _ in range(optimization_trial):
            # 探索するハイパーパラメータの範囲を作成
            weight_decay = 10 ** np.random.uniform(-8, -4)
            lr = 10 ** np.random.uniform(-6, -2)

            val_acc_list, trans_acc_list = __train(lr, weight_decay)
            key = f"lr:{lr}, weight decay:{weight_decay}"
            result_val[key] = val_acc_list
            result_trans[key] = trans_acc_list

        # 結果をグラフ表示
        import matplotlib.pylab as plt

        graph_draw_num: int = 20
        col_num: int = 5
        row_num: int = int(np.ceil(graph_draw_num / col_num))
        i: int = 0
        for key, val_acc_list in sorted(
            result_val.items(), key=lambda x: x[1][-1], reverse=True
        ):
            print(f"Best-{i+1}(val acc:{val_acc_list[-1]}) | {key}")

            plt.subplot(row_num, col_num, i + 1)
            plt.title(f"Best-{i+1}")
            plt.ylim(0.0, 1.0)
            if i % 5:
                plt.yticks([])
            plt.xticks([])
            x = np.arange(len(val_acc_list))
            plt.plot(x, val_acc_list)
            plt.plot(x, result_trans[key], "--")

            i += 1
            if i >= graph_draw_num:
                break

        plt.tight_layout()
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False
