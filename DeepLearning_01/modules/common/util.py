#!/usr/bin/env python
import numpy as np


# データセットをシャッフル
def shuffle_dataset(x, t):
    # 訓練データのデータ数でランダム配列を作る
    permutaion = np.random.permutation(x.shape[0])
    x = x[permutaion, :] if x.ndim == 2 else x[permutaion, :, :, :]
    t = t[permutaion]

    return x, t


def im2col(input_data, filter_h, filter_w, stride=1, pad=0):
    # 生成される行列は入力したデータより大きくなるのでメモリ利用量が増える

    # 4次元の各要素数を取得
    N, C, H, W = input_data.shape
    # 出力サイズを計算
    out_h: int = (H + 2 * pad - filter_h) // stride + 1
    out_w: int = (W + 2 * pad - filter_w) // stride + 1

    # input_dataの高さと幅のみパディングで拡張したinput_dataを生成
    img = np.pad(
        input_data,
        # 1次元目はデータ数なのでパディングしない
        # 2次元目はチャンネルなのでパディングしない
        # 3次元目は高さなのでパディングする
        # 4次元目は幅なのでパディングする
        pad_width=[(0, 0), (0, 0), (pad, pad), (pad, pad)],
        # パディングする値を指定
        mode="constant",
        # パディング領域は全て0にする
        constant_values=0,
    )
    # 6次元の配列を生成
    # 入力する配列に加えて出力する配列も入っている
    col = np.zeros((N, C, filter_h, filter_w, out_h, out_w))

    # 出力するデータを作成
    # 2次元の行列に変える
    # 行は出力枠,列は入力枠
    for y in range(filter_h):
        y_max = y + stride * out_h
        for x in range(filter_w):
            x_max = x + stride * out_w
            # y/xの要素にピクセルリストを設定
            # その際ストライドする
            col[:, :, y, x, :, :] = img[:, :, y:y_max:stride, x:x_max:stride]
    # colの形状
    # (データ数,チャンネル,高さ,幅,出力高さ,出力幅)
    # ↓ 以下の並びに変えている
    # (データ数,出力高さ,出力幅,チャンネル,高さ,幅)
    # その後reshape関数で行列変換している
    col = col.transpose(0, 4, 5, 1, 2, 3).reshape(N * out_h * out_w, -1)

    return col


def col2im(col, input_data, filter_h, filter_w, stride: int = 1, pad: int = 0):
    N, C, H, W = input_data
    out_h: int = (H + 2 * pad - filter_h) // stride + 1
    out_w: int = (W + 2 * pad - filter_w) // stride + 1
    col = col.reshape(N, out_h, out_w, C, filter_h, filter_w).transpose(
        0, 3, 4, 5, 1, 2
    )

    img = np.zeros((N, C, H + 2 * pad + stride - 1, W + 2 * pad + stride))
    for y in range(filter_h):
        y_max: int = y + stride * out_h
        for x in range(filter_w):
            x_max: int = x + stride * out_w
            img[:, :, y:y_max:stride, x:x_max:stride] += col[:, :, y, x, :, :]

    return img[:, :, pad : H + pad, pad : W + pad]
