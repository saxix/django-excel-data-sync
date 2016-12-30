# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import pytest
from example.models import DemoModel
from excel_data_sync.columns import Column, get_column
from excel_data_sync.validators import Rule, registry
from helperfunctions import register

logger = logging.getLogger(__name__)


def test_register_rule():
    r = Rule('ABC')
    with pytest.raises(TypeError):
        registry['test'] = r
    registry.register('test', r)
    assert registry['test'] == r

    with pytest.raises(ValueError):
        registry.register('test', 'ABC')

    with pytest.raises(ValueError):
        registry.register('test', r)

    assert registry.register('test', r, True) == r


@pytest.mark.parametrize("target", ['example.demomodel.integer',
                                    DemoModel._meta.get_field('integer')
                                    ],
                         ids=["name", "model"])
def test_register_column(target):
    class CustomColumn(Column):
        pass

    with register(target, CustomColumn):
        c = get_column(DemoModel._meta.get_field('integer'))
        assert type(c) == CustomColumn
