# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import logging
from contextlib import contextmanager


@contextmanager
def set_logging_level(level=logging.ERROR):
    backup = logging.getLogger(b'excel_data_sync').level
    logging.getLogger(b'excel_data_sync').setLevel(level)
    yield
    logging.getLogger(b'excel_data_sync').setLevel(backup)
