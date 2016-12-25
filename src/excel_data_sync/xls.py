# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

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
        options.setdefault('default_date_format', 'D-MMM-YYYY')
        options.setdefault('default_datetime_format', 'DD MMM YYYY hh:mm')
        options.setdefault('default_time_format', 'hh:mm:ss')
        self.strings_to_numbers = True
        self._vba_added = False

        # self.default_time_format =
        # self.default_datetime_format = options.pop('default_datetime_format')
        self.timezone = options.pop('timezone', pytz.utc)

        super(XlsTemplate, self).__init__(filename, options)
        self.default_datetime_format = self.add_format({'num_format': options.pop('default_datetime_format')})
        self.default_time_format = self.add_format({'num_format': options.pop('default_time_format')})

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
        if fields is None:
            fields = [field.name for field in meta.get_fields()]
        if exclude is None:
            exclude = []
        for field_name in fields:
            if field_name in exclude:
                continue
            field = meta.get_field(field_name)
            c = get_column(field)
            sheet.add_column(c)

        for i, header in enumerate(sheet.headers):
            sheet.write(0, i, header.title, header.get_format())

        for i, col in enumerate(sheet.columns):
            col.process_workbook()

        # for row in range(1, 65000):
        #     for column in sheet.columns:
        #         column.format_cell(row, column.number)
        # for row in range(1, 65000):
        for column in sheet.columns:
            column.format_column()

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(sheet.columns):
                    column.write_cell(row, colnum, record)

    # def add_worksheet(self, name=None, worksheet_class=None):
    #     """
    #     Add a new worksheet to the Excel workbook.
    #
    #     Args:
    #         name: The worksheet name. Defaults to 'Sheet1', etc.
    #
    #     Returns:
    #         Reference to a worksheet object.
    #
    #     """
    #     if worksheet_class is None:
    #         worksheet_class = self.worksheet_class
    #     return self._add_sheet(name, is_chartsheet=False, worksheet_class=worksheet_class)

    def _add_sheet(self, name, is_chartsheet=None, worksheet_class=None):
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
