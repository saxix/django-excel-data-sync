import sys


def run_tests(*test_args):
    import pytest
    pytest.main(["tests"])


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
