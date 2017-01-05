# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging

import pytest
from excel_data_sync.xls import XlsTemplate

from example.models import DemoModel
from helperfunctions import get_target_xls, get_io, _compare_xlsx_files

logger = logging.getLogger(__name__)


def compare_props(got, exp):
    return _compare_xlsx_files(got,
                               exp,
                               limit_to_files=['docProps/app.xml', 'docProps/core.xml'],
                               ignore_elements={'docProps/app.xml': ['<AppVersion']},
                               ignore_re={'docProps/app.xml': [(r'<HeadingPairs>.+?(?=</HeadingPairs>)</HeadingPairs>',
                                                                r''),
                                                               (
                                                               r'<TitlesOfParts>.+?(?=</TitlesOfParts>)</TitlesOfParts>',
                                                               r''),
                                                               ],
                                          # 'docProps/core.xml': [
                                          #     (r'<dc:description>.+?(?=</dc:description>)</dc:description>',
                                          #      r''),
                                          #     ]
    }
                               )


@pytest.mark.django_db
def test_write_properties():
    exp_filename = get_target_xls('with_properties1.xlsx')
    io = get_io(exp_filename)
    with XlsTemplate(io, properties={'title': 'title',
                                     'category': 'category',
                                     'subject': 'subject',
                                     'author': 'sax',
                                     'keywords': 'keywords',
                                     'comments': 'comment',
                                     'hyperlink_base': 'HyperlinkBase',
                                     'company': 'company',
                                     'manager': 'manager'
                                     }):
        pass

    got, exp = compare_props(io, exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_properties2():
    exp_filename = get_target_xls('with_properties2.xlsx')
    io = get_io(exp_filename)
    with XlsTemplate(io, properties={'title': 'Title2',
                                     'category': 'category2',
                                     'subject': 'subject2',
                                     'author': 'sax2',
                                     'comments': 'comment2',
                                     'keywords': 'keywords2',
                                     'hyperlink_base': 'HyperlinkBase2',
                                     'company': 'company2',
                                     'manager': 'manager2'
                                     }) as xls:
        xls.process_model(DemoModel)

    got, exp = compare_props(io, exp_filename)

    assert got == exp


@pytest.mark.django_db
def test_write_properties3():
    exp_filename = get_target_xls('with_properties3.xlsx')
    io = get_io(exp_filename)
    with XlsTemplate(io) as xls:
        xls.process_model(DemoModel)

    got, exp = compare_props(io, exp_filename)

    assert got == exp



@pytest.mark.django_db
def test_write_properties4():
    # process propoerties
    exp_filename = get_target_xls('with_properties4.xlsx')
    io = get_io(exp_filename)
    props = {"title": "{model._meta.verbose_name} data entry"}
    with XlsTemplate(io, properties=props) as xls:
        xls.process_model(DemoModel)
        xls.set_properties(props)

    got, exp = compare_props(io, exp_filename)

    assert got == exp
