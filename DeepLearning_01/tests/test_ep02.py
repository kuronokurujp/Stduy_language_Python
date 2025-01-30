#!/usr/bin/env python

# 2章 パーセプトロン
# 上記の章を呼んだ内容から作成したテストコード

def test_perceptro_system_01():
    # 論理回路ANDをパーセプトロンのアルゴリズムで実装
    def AND(x1, x2):
        # 閾値と重みのパターンは無限にある
        # 手動で調整しないといけない
        # w1, w2, theta = 0.5, 0.5, 0.7
        # w1, w2, theta = 0.5, 0.5, 0.9
        w1, w2, theta = 0.5, 0.5, 0.8
        tmp = x1 * w1 + x2 * w2
        # 敷居値を超えたら1,超えないなら0になる
        if tmp <= theta:
            return 0
        elif tmp > theta:
            return 1

    print("")
    print(AND(0, 0))
    print(AND(1, 0))
    print(AND(0, 1))
    print(AND(1, 1))


def test_perceptro_system_02():
    import numpy as np

    # AND論理回路でパーセプトロンで実装
    def AND(x1, x2):
        # 閾値を条件判定に使わないように式変更
        # 入力
        x = np.array([x1, x2])
        # 重み
        w = np.array([0.5, 0.5])
        # 閾値
        theta = 0.7
        b = -theta

        tmp = np.sum(x * w) + b
        # 閾値で比較するのではなく0以下かどうかを発火条件にしている
        if tmp <= 0:
            return 0

        return 1

    # NAND論理回路でパーセプトロンで実装
    def NAND(x1, x2):
        # 入力
        x = np.array([x1, x2])
        # 重み
        # ANDの閾値と重みを符号を反転させる事でAND結果を反転させる事ができる
        w = np.array([-0.5, -0.5])
        # 閾値
        theta = -0.7
        b = -theta

        tmp = np.sum(x * w) + b
        if tmp <= 0:
            return 0

        return 1

    # OR論理回路でパーセプトロンで実装
    def OR(x1, x2):
        # 入力
        x = np.array([x1, x2])
        # 重み
        w = np.array([0.5, 0.5])
        # 閾値
        theta = 0.2
        b = -theta

        tmp = np.sum(x * w) + b
        if tmp <= 0:
            return 0

        return 1

    def XOR(x1, x2):
        # パーセプトロンを組み合わせXOR論理回路を実装
        s1 = NAND(x1, x2)
        s2 = OR(x1, x2)
        return AND(s1, s2)

    print("AND")
    print(f"AND(0, 0) = {AND(0, 0)}")
    print(f"AND(1, 0) = {AND(1, 0)}")
    print(f"AND(0, 1) = {AND(0, 1)}")
    print(f"AND(1, 1) = {AND(1, 1)}")

    print("NAND")
    print(f"NAND(0, 0) = {NAND(0, 0)}")
    print(f"NAND(1, 0) = {NAND(1, 0)}")
    print(f"NAND(0, 1) = {NAND(0, 1)}")
    print(f"NAND(1, 1) = {NAND(1, 1)}")

    print("OR")
    print(f"OR(0, 0) = {OR(0, 0)}")
    print(f"OR(1, 0) = {OR(1, 0)}")
    print(f"OR(0, 1) = {OR(0, 1)}")
    print(f"OR(1, 1) = {OR(1, 1)}")

    print("XOR")
    print(f"XOR(0, 0) = {XOR(0, 0)}")
    print(f"XOR(1, 0) = {XOR(1, 0)}")
    print(f"XOR(0, 1) = {XOR(0, 1)}")
    print(f"XOR(1, 1) = {XOR(1, 1)}")
