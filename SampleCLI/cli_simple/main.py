import fire
from sample_module import print_test


# メイン処理関数
def main():
    fire.Fire(print_test.print_name)


if __name__ == "__main__":
    main()
