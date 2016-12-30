# -*- coding: utf-8
from __future__ import absolute_import
from django.apps import AppConfig


class XlsDataSyncConfig(AppConfig):
    name = 'excel_data_sync'

    def ready(self):
        try:
            from concurrency.fields import VersionField  # noqa
            import excel_data_sync.extras.concurrency  # noqa
        except ImportError:
            pass
