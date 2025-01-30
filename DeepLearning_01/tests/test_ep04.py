#!/usr/bin/env python
# 4章 ニューラルネットワークの学習
# 上記の章を呼んだ内容から作成したテストコード

import numpy as np
import modules.common.gradient as gradient
import modules.common.function as function
import modules.neural_net.layer as net_layer


def test_mean_squared_error():
    # 2乗和誤差の計算
    print("")

    # 1から10までの数値の中で2が正解のデータ
    t = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    # 数値の2の確率値を一番高い(0.6)ので損失関数値が小さくなる
    y = [0.1, 0.05, 0.6, 0.0, 0.05, 0.1, 0.0, 0.1, 0.0, 0.0]
    a = function.mean_squared_error(np.array(y), np.array(t))
    print(a)

    # 数値の7の確率値(0.6)が一番高く正解とは異なるので損失関数値が高い
    y = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]
    a = function.mean_squared_error(np.array(y), np.array(t))
    print(a)


def test_logarithm_show():
    # 自然対数をグラフ化

    # 0 - 1の配列を0.01刻みで配列として生成
    x = np.arange(0.0, 1.01, 0.01)
    y = np.log(x)

    import matplotlib.pyplot as pli

    pli.plot(x, y)
    pli.show()


def test_cross_entropy_error():
    # 仮で作成した訓練データの入力と教師データから交差エントロピーの計算結果を出す
    # 正解に近いほど出力結果は小さくなる

    # 1から10の中で正解が2
    t_train = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    # 数値の2の確率値が一番高いので損失関数値が小さい
    x_train = [0.1, 0.05, 0.6, 0.0, 0.05, 0.1, 0.0, 0.1, 0.0, 0.0]
    b = function.cross_entropy_error_batch(np.array(x_train), np.array(t_train))
    print(b)

    # 数値の7の確率値を一番高いので損失関数値が高い
    x_train = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]
    b = function.cross_entropy_error_batch(np.array(x_train), np.array(t_train))
    print(b)

    # 数値の7の確率値を一番高いので損失関数値が高い
    x_train = [0.1, 0.05, 0.1, 0.0, 0.05, 0.1, 0.0, 0.6, 0.0, 0.0]
    t_train = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    b = function.cross_entropy_error_batch(np.array(x_train), np.array(t_train))
    print(b)


def test_numerical_diff():
    # 微分の計算

    # xの2乗を計算
    # これに対して微分した時の値を出す
    def func(x):
        return x * x

    print("")
    # 微分の精度が悪い計算
    # 前方差分の計算で誤差の影響で結果が0になる
    v = gradient.numerical_diff_bad(func, 324)
    print(v)

    # 微分の精度が高い計算
    # 中心差分の計算で誤差を抑えている
    v = gradient.numerical_diff(func, 324)
    print(v)


def test_numerical_diff_plot():
    # 微分したのが微分元と接線しているかをグラフで表示している

    # 0.01Xの2乗 +  + 0.1x
    # 曲線の2次関数
    def function_1(x):
        return 0.01 * x**2 + 0.1 * x

    # 微分した接戦のラインを作る関数
    def tangent_line(f, x):
        d = gradient.numerical_diff(f, x)
        # 微分した直線と曲線との接線する高さを求める
        y = f(x) - d * x

        # y = ax + b
        return lambda t: d * t + y

    x = np.arange(0.0, 20.0, 0.1)
    y = function_1(x)
    import matplotlib.pylab as plt

    tf = tangent_line(function_1, 5)
    y2 = tf(x)

    tf2 = tangent_line(function_1, 10)
    y3 = tf2(x)

    plt.xlabel("x")
    plt.ylabel("f(x)")
    plt.plot(x, y)
    plt.plot(x, y2)
    plt.plot(x, y3)
    plt.show()


def test_3d_show():
    # 3次元形状をグラフで表示

    x0 = np.arange(-3, 4, 0.25)
    x1 = np.arange(-3, 4, 0.25)
    X, Y = np.meshgrid(x0, x1)
    Z = (X**2) + (Y**2)

    import matplotlib.pylab as plt

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(X, Y, Z, cmap="viridis")
    fig.colorbar(surf, shrink=0.5, aspect=5)

    ax.set_xlabel("x0")
    ax.set_ylabel("x1")
    ax.set_zlabel("f(x)")
    ax.set_label("3D Surface Plot")
    # Z軸の表示を右側から左側に見えるようにしている
    ax.view_init(elev=30, azim=45)
    # XY軸を反転させてXYともに原点から数値が増える表示にしている
    ax.invert_xaxis()
    ax.invert_yaxis()
    plt.show()


def test_partial_diff():
    # x0,x1の偏微分の計算テスト

    # 元の関数は以下
    # def function_tmp1(x0):
    #    return x0 * x0 + x1 * x1

    # x0の偏微分
    # x1を微分したくないので元の値4.0を直値している
    def function_tmp1(x0):
        return x0 * x0 + 4.0**2.0

    # x1の偏微分
    # x0を微分したくないので元の値3.0を直値している
    def function_tmp2(x1):
        return 3.0**2.0 + x1 * x1

    print("")

    v = gradient.numerical_diff(function_tmp1, 3.0)
    print(v)

    v = gradient.numerical_diff(function_tmp2, 4.0)
    print(v)


def test_numerical_gradient():
    # 配列を使って偏微分可能かテスト

    # x[0]のみ微分をしてそれが終わったらx[1]のみを微分するようにしている
    def function_2(x):
        return x[0] ** 2 + x[1] ** 2

    print(gradient.numerical_gradient_2d(function_2, np.array([3.0, 4.0])))
    print(gradient.numerical_gradient_2d(function_2, np.array([0.0, 2.0])))
    print(gradient.numerical_gradient_2d(function_2, np.array([2.0, 0.0])))


def test_numerical_gradient_plot():
    # 偏微分した結果を2Dベクトルに変換して勾配として表示

    x0 = np.arange(-2, 2.5, 0.25)
    print(f"x0={x0}")
    x1 = np.arange(-2, 2.5, 0.25)
    print(f"x1={x1}")
    # x0/x1の各軸行列を作成
    X, Y = np.meshgrid(x0, x1)
    # print(f"X={X}")
    # print(f"Y={Y}")

    # 各軸は行列になっているので一次元に変換
    X = X.flatten()
    Y = Y.flatten()
    # print(f"X.flatten()={X}")
    # print(f"Y.flatten()={Y}")

    def function_2(x):
        # XYの計算をする
        return x[0] ** 2 + x[1] ** 2

    # XY行列を作成
    n = np.array([X, Y])
    # 転置してXYペアの形にして計算して勾配値を作る
    # イメージ図
    # xのリスト,yのリストが二つ
    #   n => [[1,2,3,4],[1,2,3,4]]
    # [x,y]のペアのリスト
    #   n.T => [[1,1],[2,2],[3,3],[4,4]]
    print(f"n={n}")
    print(f"n.T={n.T}")
    grad = gradient.numerical_gradient_2d(function_2, n.T)

    # XYペアの配列をgrad[0]をX配列,grad[1]をY配列の2要素の配列にする
    # X,Y上でグラフ表示できる形にしている
    grad = grad.T
    # print(f"grad={grad}")

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


def test_gradient_descent():
    # 勾配法の計算テスト

    x = np.array([-3.0, 4.0])

    def function_2(x):
        return x[0] ** 2 + x[1] ** 2

    # パラメータを変えて結果を変えてみている
    result_01, history_01 = gradient.gradient_descent(
        function_2, init_x=x, lr=0.1, step_num=100
    )
    print(result_01)

    result_02, history_02 = gradient.gradient_descent(
        function_2, init_x=x, lr=10.0, step_num=100
    )
    print(result_02)

    result_03, history_03 = gradient.gradient_descent(
        function_2, init_x=x, lr=1e-10, step_num=100
    )
    print(result_03)


def test_gradient_descent_plot():
    # 勾配法の結果を表示
    # 勾配法の計算を進めるほど,結果が0の原点に近づいているのが分かる

    x = np.array([-3.0, 4.0])

    def function_2(x):
        # XYの計算をする
        return x[0] ** 2 + x[1] ** 2

    result_x, history_x = gradient.gradient_descent(
        function_2, init_x=x, lr=0.1, step_num=100
    )

    import matplotlib.pylab as plt

    # 勾配をベクトル表示させて勾配状態を視覚化
    # xyの最小・最大値
    plt.xlim(-3.5, 3.5)
    plt.ylim(-4.5, 4.5)

    # 破線の十字線を出す
    plt.plot([-5, 5], [0, 0], "--b")
    plt.plot([0, 0], [-5, 5], "--b")

    # 散布図で表示
    # XYの値が原点(0,0)に近づく状態を表示
    plt.plot(history_x[:, 0], history_x[:, 1], "o")

    plt.xlabel("x0")
    plt.ylabel("x1")
    plt.show()


def test_gradient_simplenet():
    # ニューラルネットワークに適切な重みパラメータを求める簡易テスト

    # 簡易ニューラルネットワーク
    class SimpleNet:
        def __init__(self):
            self.W = np.random.randn(2, 3)
            pass

        # 予測処理
        def predict(self, x):
            # 順序変えると結果が変わるので注意
            return np.dot(x, self.W)

        # 損失値を計算して出力
        def loss(self, x, t):
            z = self.predict(x)
            y = function.softmax(z)
            return function.cross_entropy_error_batch(y, t)

    net: SimpleNet = SimpleNet()
    print("")
    # 重みづけのパラメータを出力
    print(net.W)

    # 入力データ
    x = np.array([0.6, 0.9])
    # 予測値を出力
    p = net.predict(x)
    print(p)
    idx = np.argmax(p)
    print(idx)

    # 正解ラベル
    t = np.array([0, 0, 1])
    # 損失値を出力
    print(net.loss(x, t))

    # 損失から勾配値を出力
    f = lambda w: net.loss(x, t)
    dW = gradient.numerical_gradient(f, net.W)
    print(dW)


def test_twolayer_net():
    # 28 x 28画像を想定したニューラルネットワークでの学習テスト
    # ※ PC次第だが、処理時間が15分位かかるかもしれない
    # 層の数は隠れ層1つの2層のニューラルネットワーク
    # 入力のパラメータ数 = 28 * 28
    # 隠れ層のニューロン数 = 100
    # 出力のパラメータ数 = 10
    net = net_layer.TwoLayer(input_size=28 * 28, hidden_size=100, output_size=10)
    # 重みとバイアスの構造を表示
    print("")
    print(f'W1 = {net.params["W1"].shape}')
    print(f'b1 = {net.params["b1"].shape}')
    print(f'W2 = {net.params["W2"].shape}')
    print(f'b2 = {net.params["b2"].shape}')

    x = np.random.rand(100, 28 * 28)
    y = net.predict(x)
    print(f"y = {y.shape}")

    t = np.random.rand(100, 10)
    grads = net.numerical_gradient(x, t)
    print(grads["W1"].shape)
    print(grads["b1"].shape)
    print(grads["W2"].shape)
    print(grads["b2"].shape)


def test_twolayer_minibatch():
    # ミニバッチを使った2層レイヤの学習

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
        # ミニバッチを使ってニューラルネットワークの学習をする
        net = net_layer.TwoLayer(input_size=784, hidden_size=50, output_size=10)

        iters_num = 10000
        train_size = x_train.shape[0]
        batch_size = 100
        learning_rate = 0.1
        trans_loss_list = []
        for i in range(iters_num):
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            grads = net.numerical_gradient(x_batch, t_batch)
            for key in ["W1", "b1", "W2", "b2"]:
                net.params[key] -= learning_rate * grads[key]

            loss = net.loss(x_batch, t_batch)
            trans_loss_list.append(loss)

        import matplotlib.pylab as plt

        # 学習経過を表示
        plt.xlabel("itration")
        plt.ylabel("loss")
        x = np.array(len(trans_loss_list))
        plt.plot(x, trans_loss_list)
        plt.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_twolayer_epoch():
    # エポックを使った2層レイヤの学習

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
        # ミニバッチを使ってニューラルネットワークの学習をする
        net = net_layer.TwoLayer(input_size=784, hidden_size=50, output_size=10)

        iters_num = 10000
        train_size = x_train.shape[0]
        batch_size = 100
        learning_rate = 0.1
        trans_loss_list = []
        train_acc_list = []
        test_acc_list = []
        iter_per_epoch = max(train_size / batch_size, 1)
        for i in range(iters_num):
            batch_mask = np.random.choice(train_size, batch_size)
            x_batch = x_train[batch_mask]
            t_batch = t_train[batch_mask]

            grads = net.numerical_gradient(x_batch, t_batch)
            for key in ["W1", "b1", "W2", "b2"]:
                net.params[key] -= learning_rate * grads[key]

            loss = net.loss(x_batch, t_batch)
            trans_loss_list.append(loss)

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
        x = np.array(len(train_acc_list))
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
