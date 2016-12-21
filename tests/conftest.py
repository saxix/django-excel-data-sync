import os
import sys

import django_webtest
import pytest

from example.management.demo import create_sample_data


def pytest_configure(config):
    here = os.path.dirname(__file__)
    sys.path.insert(0, here)

    if config.option.log_level:
        import logging
        level = config.option.log_level.upper()
        assert level in logging._levelNames.keys()

        config = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'full': {
                    'format': '%(levelname)-7s %(name)-35s %(funcName)25s():%(lineno)s %(message)s'
                },
            },
            'handlers': {'null': {'class': 'logging.NullHandler', 'formatter': 'full'},
                         'console': {'class': 'logging.StreamHandler', 'formatter': 'full'}},
            'loggers': {
                'excel_data_sync': {
                    'handlers': ['console'],
                    'level': level
                },
            }
        }
        logging.basicConfig(**config)


def pytest_addoption(parser):
    parser.addoption('--log', default=None, action='store',
                     dest='log_level',
                     help='enable console log')


@pytest.fixture(scope='function')
def app(request):
    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()


@pytest.fixture
def data():
    create_sample_data(1)
