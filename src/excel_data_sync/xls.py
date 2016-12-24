# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import warnings

import pytz
from excel_data_sync.columns import Header, get_column
from xlsxwriter import Workbook
from xlsxwriter.chartsheet import Chartsheet
from xlsxwriter.worksheet import Worksheet

logger = logging.getLogger(__name__)


class XlsWorkSheet(Worksheet):
    def __init__(self):
        super(XlsWorkSheet, self).__init__()
        self.columns = []
        self.headers = []

    def add_column(self, column, header=None):
        column.number = len(self.columns)
        column._sheet = self
        self.columns.append(column)
        if not header:
            header = Header(column)
        self.headers.append(header)


class XlsTemplate(Workbook):
    chartsheet_class = Chartsheet
    worksheet_class = XlsWorkSheet

    def __init__(self, filename=None, options=None, properties=None):
        options = options or {}
        self.strings_to_numbers = True
        self._vba_added = False
        self.timezone = pytz.utc
        super(XlsTemplate, self).__init__(filename, options)
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

    # def add_vba(self):
    #     if not self._vba_added:
    #         self.add_vba_project(os.path.join(os.path.dirname(__file__), 'vbaProject.bin'))
    #         self._vba_added = True
    def process_model(self, model, fields=None, exclude=None, queryset=None):
        sheet = self.add_worksheet(model._meta.model_name)
        meta = model._meta
        if exclude is None:
            exclude = []
        for field in meta.get_fields():
            if field.name in exclude:
                continue
            if fields and field.name not in fields:
                continue
            c = get_column(field)
            sheet.add_column(c)

        for i, header in enumerate(sheet.headers):
            sheet.write(0, i, header.title, header.get_format(self))

        for i, col in enumerate(sheet.columns):
            col.process_workbook(sheet)

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(sheet.columns):
                    v = column.get_value_from_object(record)
                    sheet.write(row, colnum, v, column.get_format(self))

    def add_worksheet(self, name=None, worksheet_class=None):
        """
        Add a new worksheet to the Excel workbook.

        Args:
            name: The worksheet name. Defaults to 'Sheet1', etc.

        Returns:
            Reference to a worksheet object.

        """
        if worksheet_class is None:
            worksheet_class = self.worksheet_class
        return self._add_sheet(name, is_chartsheet=False, worksheet_class=worksheet_class)

    def _add_sheet(self, name, is_chartsheet=None, worksheet_class=None):
        if is_chartsheet is not None:
            warnings.warn(
                "'is_chartsheet' has been deprecated and "
                "will be removed in the next versions. Use proper 'worksheet_class' to get same result",
                PendingDeprecationWarning)
        if is_chartsheet is None and worksheet_class is None:
            raise ValueError("You must provide 'is_chartsheet' or 'worksheet_class'")
        if worksheet_class:
            worksheet = worksheet_class()
        else:
            if is_chartsheet:
                worksheet = self.chartsheet_class()
            else:
                worksheet = self.worksheet_class()

        sheet_index = len(self.worksheets_objs)
        name = self._check_sheetname(name, isinstance(worksheet, Chartsheet))

        # Initialization data to pass to the worksheet.
        init_data = {
            'name': name,
            'index': sheet_index,
            'str_table': self.str_table,
            'worksheet_meta': self.worksheet_meta,
            'optimization': self.optimization,
            'tmpdir': self.tmpdir,
            'date_1904': self.date_1904,
            'strings_to_numbers': self.strings_to_numbers,
            'strings_to_formulas': self.strings_to_formulas,
            'strings_to_urls': self.strings_to_urls,
            'nan_inf_to_errors': self.nan_inf_to_errors,
            'default_date_format': self.default_date_format,
            'default_url_format': self.default_url_format,
            'excel2003_style': self.excel2003_style,
            'remove_timezone': self.remove_timezone,
        }

        worksheet._initialize(init_data)
        worksheet._book = self
        self.worksheets_objs.append(worksheet)
        self.sheetnames[name] = worksheet

        return worksheet

    def __del__(self):
        """Close file in destructor if it hasn't been closed explicitly."""
        try:
            if not self.fileclosed and self.filename:
                self.close()
        except:
            raise Exception("Exception caught in workbook destructor. "
                            "Explicit close() may be required for workbook.")
