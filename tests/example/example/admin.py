# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.admin import ModelAdmin, site
from example.models import DemoModel, Option, UserDetail
from excel_data_sync.admin import XlsDataSyncAdminMixin, export_records


class UserDetailModelAdmin(ModelAdmin):
    list_display = [f.name for f in UserDetail._meta.fields]


class DemoModelAdmin(XlsDataSyncAdminMixin, ModelAdmin):
    list_display = [f.name for f in DemoModel._meta.fields]
    actions = [export_records]


class OptionAdmin(ModelAdmin):
    list_display = ['name']


site.register(DemoModel, DemoModelAdmin)
site.register(UserDetail, UserDetailModelAdmin)
site.register(Option, OptionAdmin)
