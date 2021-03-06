# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
from six import BytesIO

import pytest
from example.models import DemoModel
from excel_data_sync.xls import XlsTemplate

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_base():
    with XlsTemplate(BytesIO()) as xls:
        xls.process_model(DemoModel)

    headers = xls.worksheets_objs[0].headers
    assert headers[0]._get_format().num_format == ''
