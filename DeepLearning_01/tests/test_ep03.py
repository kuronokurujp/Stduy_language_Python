#!/usr/bin/env python

# 3章 ニューラルネットワーク
# 上記の章を呼んだ内容から作成したテストコード

import numpy as np
import modules.dataset.mnist as mnist


# 何もしない活性関数
def identity_function(x):
    return x


# ステップ活性関数
def step_function(x):
    return np.array(x > 0, dtype=int)


# シグモイド活性関数
def sigmoid_function(x):
    return 1.0 / (1.0 + np.exp(-x))


# ReLU活性関数
def relu_function(x):
    return np.maximum(0, x)


# ソフトマックス活性関数
# 計算精度が悪い版
def softmax_bad_function(x):
    exp_a = np.exp(x)
    sum_exp_a = np.sum(exp_a)
    return exp_a / sum_exp_a


# ソフトマックス活性関数
def softmax_function(a):
    # 配列の中で最大値を定数値とする
    max = np.max(a)
    exp_a = np.exp(a - max)
    sum_exp_a = np.sum(exp_a)
    return exp_a / sum_exp_a


def test_step_function():
    import matplotlib.pylab as plt

    # ステップ関数の結果をグラフ表示

    # xの値が0を超えたらyの値が1になる
    # xの値が0以下ならyの値が0になる
    x = np.arange(-5.0, 5.0, 0.1)
    y = step_function(x)
    plt.plot(x, y)
    plt.ylim(-0.1, 1.1)
    plt.show()


def test_sigmoid_function():
    import matplotlib.pylab as plt

    # シグモイド関数の結果をグラフ表示
    x = np.arange(-5.0, 5.0, 0.1)
    y = sigmoid_function(x)
    plt.plot(x, y)
    plt.ylim(-0.1, 1.1)
    plt.show()


def test_relu_function():
    import matplotlib.pylab as plt

    # ReLu関数の結果をグラフ表示
    x = np.arange(-5.0, 5.0, 0.1)
    y = relu_function(x)
    plt.plot(x, y)
    plt.show()


def test_neural_network_3_layer():
    # 3層のニューラルネットワーク
    def init_newwork():
        network = {}
        # 各層の重みとバイアスを作成
        # 行列計算するので配列同時の掛け算で左辺の列と右辺の行の数が一致していないとエラーになる

        # 入力層からレイヤ1層の重みとバイアス
        network["W1"] = np.array([[0.1, 0.3, 0.5], [0.2, 0.4, 0.6]])
        network["b1"] = np.array([0.1, 0.2, 0.3])

        # レイヤ1層からレイヤ2層の重みとバイアス
        network["W2"] = np.array([[0.1, 0.4], [0.2, 0.5], [0.3, 0.6]])
        network["b2"] = np.array([0.1, 0.2])

        # レイヤ2層から出力層の重みとバイアス
        network["W3"] = np.array([[0.1, 0.3], [0.2, 0.4]])
        network["b3"] = np.array([0.1, 0.2])

        return network

    def forward(network, x):
        # 各層の重みとバイアスを取得
        W1, W2, W3 = network["W1"], network["W2"], network["W3"]
        b1, b2, b3 = network["b1"], network["b2"], network["b3"]

        # 各層での計算
        # 入力層から第1層の信号
        a1 = np.dot(x, W1) + b1
        z1 = sigmoid_function(a1)

        # 第1層から第2層の信号
        a2 = np.dot(z1, W2) + b2
        z2 = sigmoid_function(a2)

        # 第2層から出力層の信号
        a3 = np.dot(z2, W3) + b3
        # 最後の出力層の活性関数は恒等関数を使う
        y = identity_function(a3)

        return y

    network = init_newwork()
    # x = np.array([1.0, 0.5])
    # x = np.array([0.3, 0.5])
    # x = np.array([1.3, 0.2])
    x = np.array([100.3, 0.2])
    # 結果が1を超えることはない
    y = forward(network=network, x=x)
    print(y)


def test_softmax():
    # 計算精度が悪いソフトマックス関数を使った場合
    # 結果がnanになる
    a = np.array([1010, 1000, 990])
    v = softmax_bad_function(a)
    print("")
    print(f"values={a}")
    print(f"softmax bat result={v}")

    v = softmax_function(a)
    print(f"values={a}")
    print(f"softmax good result={v}")
    # ソフトマックス関数で計算した各要素を総和したのは必ず1になる!
    print(np.sum(v))

    a = np.array([0.3, 2.9, 4.0])
    print(f"values={a}")
    v = softmax_function(a)
    print(f"softmax good result={v}")


def test_mnist_show():
    # 機械学習する手書きの数字画像の訓練とテストデータをダウンロードしてパラメータを表示

    import pathlib as path
    import numpy as np
    import os
    from PIL import Image

    try:
        # ダウンロード先のディレクトリを絶対パスで生成
        data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
        data_path = data_path.joinpath("data/test_ep03/")
        mnist.init_mnist(download_path=data_path)

        # ダウンロードする
        (x_train, t_train), (x_test, t_test) = mnist.load_mnist(
            flatten=True, normalize=False
        )

        # ダウンロードした手書きデータを画像に変換して表示
        img: np = x_train[0]
        label: np = t_train[0]
        print(f"label={label}")
        print(f"label len={len(t_train)}")

        print(f"img.shape {img.shape}")
        img = img.reshape(28, 28)
        print(f"img.shape {img.shape}")
        pil_img = Image.fromarray(np.uint8(img))
        pil_img.show()

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_mnist_check():
    # 用意された文字認識のモデルデータを使って認識テスト

    import pathlib as path
    import numpy as np
    import os

    try:
        # 訓練データとラベルを取得
        def get_data():
            (x_train, t_train), (x_test, t_test) = mnist.load_mnist(
                flatten=True, normalize=True, one_hot_label=False
            )
            return x_train, t_train

        def init_network():
            import pickle

            # 機械学習する手書きの数字画像の訓練とテストデータをダウンロード
            # ダウンロード先のディレクトリを絶対パスで生成
            data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
            data_path = data_path.joinpath("data/test_ep03/")
            mnist.init_mnist(download_path=data_path)

            # サンプルの重みとバイアスを取得
            weight_pkl_path = data_path.joinpath("sample_weight.pkl")
            with open(weight_pkl_path.as_posix(), "rb") as f:
                network = pickle.load(f)

            return network

        def predict(network, x):
            # 各層の重みとバイアスを取得
            W1, W2, W3 = network["W1"], network["W2"], network["W3"]
            b1, b2, b3 = network["b1"], network["b2"], network["b3"]

            # 各層での計算
            # 入力層から第1層の信号
            a1 = np.dot(x, W1) + b1
            z1 = sigmoid_function(a1)

            # 第1層から第2層の信号
            a2 = np.dot(z1, W2) + b2
            z2 = sigmoid_function(a2)

            # 第2層から出力層の信号
            a3 = np.dot(z2, W3) + b3
            # 最後の出力層の活性関数は恒等関数を使う
            y = softmax_function(a3)

            return y

        network = init_network()
        x, t = get_data()

        accuracy_cnt = 0
        # 画像データを一つずつ取り出して推論している
        for i in range(len(x)):
            # 数字画像データから推論して要素10個の配列を出力
            y = predict(network=network, x=x[i])
            # 配列中で一番高い値のインデックスを取得
            p = np.argmax(y)

            # 正解データと比較して正しいなら正解カウント+1する
            if t[i] == p:
                accuracy_cnt += 1

        # 予測精度を表示(1に近づくほど精度が高い)
        print(f"Accuracy: {float(accuracy_cnt)/ len(x)}")

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False


def test_mnist_check_batch():
    # 学習データを全て使って推論するのではなく,
    # 指定数(バッチサイズ)のみで推論して全て使った時と近い結果を出す
    # 学習データを全て使うのではないので学習時間が減らせる

    import pathlib as path
    import numpy as np
    import os

    try:
        # 訓練データとラベルを取得
        def get_data():
            (x_train, t_train), (x_test, t_test) = mnist.load_mnist(
                flatten=True, normalize=True, one_hot_label=False
            )
            return x_train, t_train

        def init_network():
            import pickle

            # 機械学習する手書きの数字画像の訓練とテストデータをダウンロード
            # ダウンロード先のディレクトリを絶対パスで生成
            data_path = path.Path(os.path.dirname(os.path.abspath(__file__)))
            data_path = data_path.joinpath("data/test_ep03/")
            mnist.init_mnist(download_path=data_path)

            weight_pkl_path = data_path.joinpath("sample_weight.pkl")
            with open(weight_pkl_path.as_posix(), "rb") as f:
                network = pickle.load(f)

            return network

        def predict(network, x):
            # 各層の重みとバイアスを取得
            W1, W2, W3 = network["W1"], network["W2"], network["W3"]
            b1, b2, b3 = network["b1"], network["b2"], network["b3"]

            # 各層での計算
            # 入力層から第1層の信号
            a1 = np.dot(x, W1) + b1
            z1 = sigmoid_function(a1)

            # 第1層から第2層の信号
            a2 = np.dot(z1, W2) + b2
            z2 = sigmoid_function(a2)

            # 第2層から出力層の信号
            a3 = np.dot(z2, W3) + b3
            # 最後の出力層の活性関数は恒等関数を使う
            y = softmax_function(a3)

            return y

        network = init_network()
        x, t = get_data()

        accuracy_cnt = 0
        # バッチ処理で処理を一括化する
        batch_size: int = 100
        for i in range(0, len(x), batch_size):
            # 学習データをバッチサイズ分まとめて、一括で推論する
            x_batch = x[i : i + batch_size]
            y_batch = predict(network=network, x=x_batch)
            # batch_sizeのそれぞれの配列の中で一番高い値インデックスを取得
            p = np.argmax(y_batch, axis=1)

            # 正解データと比較して正しいなら正解カウントを上げる
            accuracy_cnt += np.sum(p == t[i : i + batch_size])

        # 予測精度を表示(1に近づくほど精度が高い)
        print(f"Accuracy: {float(accuracy_cnt)/ len(x)}")

    except FileNotFoundError as ex:
        print(ex)
        assert False
    except Exception as ex:
        print(ex)
        assert False
