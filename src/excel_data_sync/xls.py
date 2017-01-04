# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import os
from datetime import datetime

import pytz
from django.db.models import NOT_PROVIDED
from excel_data_sync.columns import Header, get_column
from xlsxwriter import Workbook
from xlsxwriter.chartsheet import Chartsheet
from xlsxwriter.worksheet import Worksheet

logger = logging.getLogger(__name__)


class XlsRuleSheet(Worksheet):
    is_rule = True
    NULL = 1
    BLANK = 2
    UNIQUE = 3
    REQUIRED = 4
    DEFAULT = 5
    MAX_LENGTH = 6
    PRIMARY_KEY = 7
    EDITABLE = 8

    def _initialize(self, init_data):
        super(XlsRuleSheet, self)._initialize(init_data)
        self.write(self.NULL, 0, 'null')
        self.write(self.BLANK, 0, 'blank')
        self.write(self.REQUIRED, 0, 'required')
        self.write(self.UNIQUE, 0, 'unique')
        self.write(self.DEFAULT, 0, 'default')
        self.write(self.MAX_LENGTH, 0, 'max_length')
        self.write(self.PRIMARY_KEY, 0, 'primary_key')
        self.write(self.EDITABLE, 0, 'editable')
        if self._book.hide:
            self.hide()

    def add_column(self, column):
        self.write(0, column.number + 1, column.header.title)
        self.write_boolean(self.NULL, column.number + 1, column.field.null)
        self.write_boolean(self.BLANK, column.number + 1, column.field.blank)
        self.write_boolean(self.UNIQUE, column.number + 1, column.field.unique)
        if column.field.max_length:
            self.write_number(self.MAX_LENGTH, column.number + 1, column.field.max_length)
        self.write_boolean(self.PRIMARY_KEY, column.number + 1, column.field.max_length)
        self.write_boolean(self.EDITABLE, column.number + 1, column.field.max_length)

        default = column.field.default
        if not default == NOT_PROVIDED:
            if callable(default):
                value = str(default())
            else:
                value = str(default)
            self.write(self.DEFAULT, column.number + 1, value)


class XlsWorkSheet(Worksheet):
    def __init__(self):
        super(XlsWorkSheet, self).__init__()
        self.columns = []
        self.headers = []

    def _initialize(self, init_data):
        super(XlsWorkSheet, self)._initialize(init_data)

    def add_column(self, column, header=None):
        column.number = len(self.columns)
        column._sheet = self
        self.columns.append(column)
        if column.need_vba:
            self._book.add_vba()

        if not header:
            header = Header(column)
        self.headers.append(header)
        self.rules.add_column(column)

    def write_columns(self):
        for i, header in enumerate(self.headers):
            self.write(0, i, header.title, header._get_format())
            help = str(header.column.field.help_text)
            if help:
                self.write_comment(0, i, help)
            header.column.format_column()
            header.column.add_data_validation()


class XlsTemplate(Workbook):
    chartsheet_class = Chartsheet
    worksheet_class = XlsWorkSheet
    header_class = Header

    def __init__(self, filename=None, options=None, properties=None,
                 protect=True, hide=True, header_class=None, **kwargs):
        options = options or {}
        options.setdefault('default_date_format', 'D-MMM-YYYY')
        options.setdefault('default_datetime_format', 'DD MMM YYYY hh:mm')
        options.setdefault('default_time_format', 'hh:mm:ss')
        options.setdefault('strings_to_numbers', True)

        self._vba_added = False
        self.protect = protect
        self.hide = hide
        self.timezone = options.pop('timezone', pytz.utc)

        self.header_class = header_class or self.header_class

        super(XlsTemplate, self).__init__(filename, options)

        self.default_datetime_format = self.add_format({'locked': False, 'num_format': options.pop('default_datetime_format')})
        self.default_time_format = self.add_format({'locked': False, 'num_format': options.pop('default_time_format')})
        self.default_date_format = self.add_format({'locked': False, 'num_format': options.pop('default_date_format')})

        if properties:
            self.set_properties(properties)
        self.set_custom_property("Creation Date", datetime.today(), "date")

        self.define_name('THIS', '=!A1')
        self.define_name('THIS_COL', '=!A')

    def add_vba(self):
        if not self._vba_added:
            self.add_vba_project(os.path.join(os.path.dirname(__file__), 'vbaProject.bin'))
            self._vba_added = True

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

        sheet.write_columns()

        # for i, col in enumerate(sheet.columns):
        #     col.add_data_validation()

        # for column in sheet.columns:
        #     column.format_column()

        if queryset:
            for row, record in enumerate(queryset, 1):
                for colnum, column in enumerate(sheet.columns):
                    column.write_cell(row, colnum, record)

    def _add_rule_sheet(self, owner):
        rulesheet = XlsRuleSheet()
        sheet_index = len(self.worksheets_objs)
        name = "{}.__rules__".format(owner.name)
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
        rulesheet._book = self
        rulesheet._initialize(init_data)

        self.worksheets_objs.append(rulesheet)
        self.sheetnames[name] = rulesheet
        owner.rules = rulesheet

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

        if self.protect:
            worksheet.protect()

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
        self._add_rule_sheet(worksheet)
        return worksheet

    def __del__(self):
        """Close file in destructor if it hasn't been closed explicitly."""
        try:
            if not self.fileclosed and self.filename:
                self.close()
        except:
            raise Exception("Exception caught in workbook destructor. "
                            "Explicit close() may be required for workbook.")
