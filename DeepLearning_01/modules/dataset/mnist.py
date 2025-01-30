# coding: utf-8
try:
    import urllib.request
except ImportError:
    raise ImportError("You should use Python 3.x")
import os.path
import pathlib as path
import gzip
import pickle
import os
import numpy as np


# 公式からMNISTデータセットが取得できないので以下のミラーサイトを使う
url_base = "https://ossci-datasets.s3.amazonaws.com/mnist/"

key_file = {
    "train_img": "train-images-idx3-ubyte.gz",
    "train_label": "train-labels-idx1-ubyte.gz",
    "test_img": "t10k-images-idx3-ubyte.gz",
    "test_label": "t10k-labels-idx1-ubyte.gz",
}

# MNISTのデータファイルを保管するディレクトリパス
dataset_dir = None
# MINISTのモデルファイル
save_file = None

# 縦*横の画像サイズ
img_size = 28 * 28


def __download(file_name):
    file_path = dataset_dir + "/" + file_name

    if os.path.exists(file_path):
        return

    print("Downloading " + file_name + " ... ")
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
    }
    request = urllib.request.Request(url_base + file_name, headers=headers)
    response = urllib.request.urlopen(request).read()
    with open(file_path, mode="wb") as f:
        f.write(response)
    print("Done")


def __download_mnist():
    for v in key_file.values():
        __download(v)


def __load_label(file_name):
    file_path = dataset_dir + "/" + file_name

    print("Converting " + file_name + " to NumPy Array ...")
    with gzip.open(file_path, "rb") as f:
        labels = np.frombuffer(f.read(), np.uint8, offset=8)
    print("Done")

    return labels


def __load_img(file_name):
    file_path = dataset_dir + "/" + file_name

    print("Converting " + file_name + " to NumPy Array ...")
    with gzip.open(file_path, "rb") as f:
        data = np.frombuffer(f.read(), np.uint8, offset=16)
    data = data.reshape(-1, img_size)
    print("Done")

    return data


def __convert_numpy():
    dataset = {}
    dataset["train_img"] = __load_img(key_file["train_img"])
    dataset["train_label"] = __load_label(key_file["train_label"])
    dataset["test_img"] = __load_img(key_file["test_img"])
    dataset["test_label"] = __load_label(key_file["test_label"])

    return dataset


def init_mnist(download_path: path.Path):
    global dataset_dir
    global save_file

    dataset_dir = download_path.absolute().as_posix()
    os.makedirs(dataset_dir, exist_ok=True)

    save_file = dataset_dir + "/mnist.pkl"

    __download_mnist()
    dataset = __convert_numpy()
    print("Creating pickle file ...")
    with open(save_file, "wb") as f:
        pickle.dump(dataset, f, -1)
    print("Done!")


def __change_one_hot_label(X):
    T = np.zeros((X.size, 10))
    for idx, row in enumerate(T):
        row[X[idx]] = 1

    return T


def load_mnist(normalize=True, flatten=True, one_hot_label=False):
    if not os.path.exists(save_file):
        raise FileNotFoundError(f"not exist = {save_file}")

    with open(save_file, "rb") as f:
        dataset = pickle.load(f)

    # データを0-1で正規化
    if normalize:
        for key in ("train_img", "test_img"):
            dataset[key] = dataset[key].astype(np.float32)
            dataset[key] /= 255.0

    # ラベルをonehotに
    if one_hot_label:
        dataset["train_label"] = __change_one_hot_label(dataset["train_label"])
        dataset["test_label"] = __change_one_hot_label(dataset["test_label"])

    # 画像データの形状を縦横に変える
    if not flatten:
        for key in ("train_img", "test_img"):
            dataset[key] = dataset[key].reshape(-1, 1, 28, 28)

    # 訓練とテストデータを出力
    return (dataset["train_img"], dataset["train_label"]), (
        dataset["test_img"],
        dataset["test_label"],
    )


if __name__ == "__main__":
    init_mnist()
