import pytest

from cli_simple.sample_module2 import add_test

def test_is_even():
    flg: bool = add_test.add_test(1, 1) == 2
    assert flg

def test_collatz():
    pass
