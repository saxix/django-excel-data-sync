# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from django.db import models
from example.models import DemoModel
from excel_data_sync.inspector import process_model
from helperfunctions import _compare_xlsx_files, get_io, get_target_xls

logger = logging.getLogger(__name__)


# @pytest.mark.django_db
# def test_1():
#     G(Option, n=10)
#     exp_filename = os.path.join(here, 'data', 'test.xls')
#     process_model(DemoModel, exp_filename)

def test_write_boolean():
    class BooleanModel(models.Model):
        field = models.BooleanField()

        class Meta:
            app_label = 'test'

    exp_filename = get_target_xls('booleanmodel.xls')
    io = get_io(exp_filename)
    process_model(BooleanModel, io)
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_foreignkey(data):
    exp_filename = get_target_xls('test.xls')
    io = get_io(exp_filename)
    process_model(DemoModel, io)
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_data(data):
    exp_filename = get_target_xls('test_data.xls')
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  exclude=['email', 'option', 'uuid'],
                  queryset=DemoModel.objects.all())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_enable_vba(data):
    exp_filename = get_target_xls('test_vba.xls')
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  exclude=['email'],
                  options={'vba': True})
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_properties(data):
    exp_filename = get_target_xls('test_properties.xls')
    io = get_io(exp_filename)
    process_model(DemoModel, io,
                  exclude=['email'],
                  properties={'title': 'Title'})
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
