#
import os
from sample_module2 import add_test


def print_test():
    print("print_test")


def print_name(name="world"):
    print("hello {}".format(name))


if __name__ == "__main__":
    print_name(name=os.getcwd())
