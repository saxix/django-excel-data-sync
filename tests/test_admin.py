# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import six

import pytest

from helperfunctions import _compare_xlsx_files, get_target_xls

try:
    from django.urls import reverse
except:
    from django.core.urlresolvers import reverse


logger = logging.getLogger(__name__)


admin_extra_urls = pytest.importorskip("admin_extra_urls")


def test_export_template_validate(app, admin_user, data):
    url = reverse('admin:example_demomodel_changelist')

    res = app.get(url, user=admin_user.username)
    res = res.click('Get Xls Template')

    res.form['filename'] = 'name'
    res = res.form.submit('apply')
    assert res.status_code == 200
    assert res.context['form'].errors == {'columns': [u'This field is required.']}


def test_export_template(app, admin_user, data):
    url = reverse('admin:example_demomodel_changelist')

    res = app.get(url, user=admin_user.username)
    res = res.click('Get Xls Template')

    res.form['filename'] = 'name'
    res.form['columns'] = ['email', 'range_5_10']
    res = res.form.submit('apply')

    exp_filename = get_target_xls('test_admin_export.xls')
    io = six.BytesIO(res.content)
    # open(exp_filename, 'wb').write(io.read())
    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp
    assert res.status_code == 200
    assert res['Content-Type'] == 'application/vnd.ms-excel'


def test_export_records(app, admin_user, data):
    url = reverse('admin:example_demomodel_changelist')

    res = app.get(url, user=admin_user.username)

    form = res.forms['changelist-form']
    form['action'] = 'export_records'
    form.set('_selected_action', True, 0)
    res = form.submit()

    res.form['filename'] = 'name'
    res.form['columns'] = ['id', 'range_5_10']
    res = res.form.submit('apply')

    exp_filename = get_target_xls('test_admin_export_records.xls')
    io = six.BytesIO(res.content)
    # open(exp_filename, 'wb').write(io.read())
    assert res.status_code == 200
    assert res['Content-Type'] == 'application/vnd.ms-excel'

    got, exp = _compare_xlsx_files(io,
                                   exp_filename)

    assert got == exp


def test_export_records_validate(app, admin_user, data):
    url = reverse('admin:example_demomodel_changelist')

    res = app.get(url, user=admin_user.username)
    form = res.forms['changelist-form']
    form['action'] = 'export_records'
    form.set('_selected_action', True, 0)
    res = form.submit()

    res.form['filename'] = 'name'
    res = res.form.submit('apply')
    assert res.status_code == 200
    assert res.context['form'].errors == {'columns': [u'This field is required.']}
