# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os

from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from xlsxwriter.chartsheet import Chartsheet

logger = logging.getLogger(__name__)


class XlsWorkSheet(Worksheet):
    pass


class XlsTemplate(Workbook):
    chartsheet_class = Chartsheet
    worksheet_class = XlsWorkSheet

    def __init__(self, filename=None, options=None, properties=None):
        options = options or {}
        vba = options.pop('vba', False)
        # options = options or {'remove_timezone': True}
        super(XlsTemplate, self).__init__(filename, options)
        if vba:
            self.add_vba_project(os.path.join(os.path.dirname(__file__), 'vbaProject.bin'))

        if properties:
            self.set_properties(properties)
            # self.set_properties({
            # 'title':    'This is an example spreadsheet',
            # 'subject':  'With document properties',
            # 'author':   'John McNamara',
            # 'manager':  'Dr. Heinz Doofenshmirtz',
            # 'company':  'of Wolves',
            # 'category': 'Example spreadsheets',
            # 'keywords': 'Sample, Example, Properties',
            # 'status': '',
            # 'comments': 'Created with Python and XlsxWriter'
        # })
        # self.set_custom_property("Creation Date", datetime.today(), "date")

        self.define_name('THIS', '=!A1')
        self.define_name('THIS_COL', '=!A')
        #
        # self.unlocked = self.add_format({'locked': 0})
        # self.locked = self.add_format({'locked': 1})
        # self.hidden = self.add_format({'hidden': 1})
