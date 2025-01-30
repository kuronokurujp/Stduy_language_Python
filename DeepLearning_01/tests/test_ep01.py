#!/usr/bin/env python

# 1章 Python入門
# 上記の章を呼んだ内容から作成したテストコード


def test_list():
    # リストについてテスト

    a: list = [1, 2, 3]
    # リストの並びが逆順
    # [3, 2, 1]
    print(a[::-1])

    # リスト内の全要素を取りだして表示
    # 1
    # 2
    # 3
    for v in a:
        print(v)


def test_numpy():
    # numpyについてのテスト

    import numpy as np

    # 1次元の配列
    x = np.array([1.0, 2.0, 3.0])
    print(f"x={x}")

    # 2次元の配列
    x = np.array([[3, 23, 3, 6], [1, 5, 4, 9]])
    # xの行の要素数
    size = x.shape[0]
    print(f"size={size}")

    arange = np.arange(size)
    print(f"arange={arange}")

    # tはxのインデックスのリスト t= np.array([xの1次元内のインデックス,xの2次元内のインデックス])
    t = np.array([[3, 0], [1, 2], [0, 3]])
    z = x[arange, t]

    print(f"s.shape={z.shape}")
    print(f"z={z}")


def test_matplotlib():
    # グラフ表示テスト

    import numpy as np
    import matplotlib.pyplot as pli

    # 0 - 6までの値を0.1刻みで増えていく要素の配列を生成
    x = np.arange(0, 6, 0.1)
    # y軸の配列を生成
    y1 = np.sin(x)
    y2 = np.cos(x)

    # グラフ描画
    pli.plot(x, y1, label="sin")
    # 破線で表示
    pli.plot(x, y2, linestyle="--", label="cos")
    # 各軸のラベル設定
    pli.xlabel("x")
    pli.ylabel("y")
    # タイトル設定
    pli.title("sin & cos")
    # ラベルの表記
    pli.legend()
    # 表示
    pli.show()


def test_mkdir():
    # フォルダ生成のテスト

    import pathlib as path
    import os

    file_name: path.Path = path.Path(os.path.dirname(os.path.abspath(__file__)))
    file_name = file_name.joinpath("data/test_ep01/params.pk1")

    # 親ディレクトリ「test_ep01」がない場合は作成
    if file_name.is_dir():
        file_name.mkdir(parents=True, exist_ok=True)
    else:
        file_name.parent.mkdir(parents=True, exist_ok=True)
