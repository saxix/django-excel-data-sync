# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import six

import pytest
from django.core import management

logger = logging.getLogger(__name__)


@pytest.mark.django_db
def test_create_xls_template():
    out = six.StringIO()
    management.call_command('create-xls-template', 'example.demomodel', stdout=out)
    assert out.getvalue() == 'Saved..example.demomodel.xls\n'


@pytest.mark.django_db
def test_create_xls_template_data(data):
    out = six.StringIO()
    management.call_command('create-xls-template', 'example.demomodel', data=True, stdout=out)
    assert out.getvalue() == 'Saved..example.demomodel.xls\nDumped 1 records\n'
