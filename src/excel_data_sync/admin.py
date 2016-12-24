# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging
import six

import pytz
from django import forms
from django.conf import settings
from django.contrib.admin import helpers
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
# from excel_data_sync.inspector import process_model
from excel_data_sync.xls import XlsTemplate

try:
    from admin_extra_urls.extras import ExtraUrlMixin, link
except ImportError:
    ExtraUrlMixin = object

    def link():
        def inner(func):
            return func

        return inner

logger = logging.getLogger(__name__)

DATE_FORMATS = ['DD-MMM-YYYY',
                'M/D/YY',
                'DD-MMM-YY',
                'D-MMM',
                'MMM-YY',
                ]
TIME_FORMATS = ['h:mm AM/PM',
                'h:mm:ss AM/PM',
                'h:mm',
                'h:mm:ss',
                ]
DATETIME_FORMATS = ['DD-MMM-YYYY hh:mm',
                    'DD-MM-YYYY hh:mm']


class XlsDataSyncOptionForm(forms.Form):
    filename = forms.CharField(label=_('Filename'))
    # require_vba = forms.BooleanField(label=_('Require VBA'), required=False)
    timezone = forms.ChoiceField(choices=zip(pytz.all_timezones, pytz.all_timezones),
                                 initial=settings.TIME_ZONE)
    date_format = forms.ChoiceField(choices=zip(DATE_FORMATS, DATE_FORMATS),
                                    initial=DATE_FORMATS[0])
    datetime_format = forms.ChoiceField(choices=zip(DATETIME_FORMATS, DATETIME_FORMATS),
                                        initial=DATETIME_FORMATS[0])
    time_format = forms.ChoiceField(choices=zip(TIME_FORMATS, TIME_FORMATS),
                                    initial=TIME_FORMATS[0])
    columns = forms.MultipleChoiceField(widget=FilteredSelectMultiple(
        _('Columns'),
        False,
        attrs={'size': 30}))

    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model')
        cols = sorted([(f.name, f.verbose_name) for f in model._meta.fields])
        super(XlsDataSyncOptionForm, self).__init__(*args, **kwargs)
        self.fields['columns'].choices = cols

    @property
    def media(self):
        extra = '' if settings.DEBUG else '.min'
        js = ['vendor/jquery/jquery%s.js' % extra, 'jquery.init.js',
              'inlines%s.js' % extra]
        js.extend(['SelectBox.js', 'SelectFilter2.js'])
        return forms.Media(js=['admin/js/%s' % url for url in js])


class XlsDataSyncActionOptionForm(XlsDataSyncOptionForm):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    select_across = forms.BooleanField(label='', required=False, initial=0,
                                       widget=forms.HiddenInput({'class': 'select-across'}))
    action = forms.CharField(label='', required=True, initial='', widget=forms.HiddenInput())


class XlsDataSyncAdminMixin(ExtraUrlMixin):
    @csrf_exempt
    @link()
    def get_xls_template(self, request):
        model = self.model

        if 'apply' in request.POST:
            form = XlsDataSyncOptionForm(request.POST, model=model)
            if form.is_valid():
                filename = form.cleaned_data['filename']
                fields = form.cleaned_data['columns']
                timezone = form.cleaned_data['timezone']
                date_format = form.cleaned_data['date_format']
                out = six.BytesIO()
                with XlsTemplate(out, {'default_date_format': date_format,
                                       'timezone': timezone}) as xls:
                    xls.process_model(model,
                                      fields=fields)
                out.seek(0)
                response = HttpResponse(out.read(),
                                        content_type="application/vnd.ms-excel"
                                        )
                response['Content-Disposition'] = six.b('attachment;filename="%s"' % filename)
                return response
        else:
            filename = '{}.xls'.format(model._meta.model_name)
            form = XlsDataSyncOptionForm(initial={'filename': filename, },
                                         model=model)
        media = self.media + form.media
        ctx = {
            'form': form,
            'change': True,
            'action_short_description': _('Generate Excel Template'),
            'title': _('Generate Excel Template'),
            'is_popup': False,
            'action': _('Generate Template'),
            'opts': model._meta,
            'app_label': model._meta.app_label,
            'media': mark_safe(media)}
        ctx.update(self.admin_site.each_context(request))

        return render(request,
                      'excel_data_sync/options.html',
                      ctx)


def get_action(request):
    try:
        action_index = int(request.POST.get('index', 0))
    except ValueError:  # pragma: no-cover
        action_index = 0
    return request.POST.getlist('action')[action_index]


def export_records(modeladmin, request, queryset):
    model = modeladmin.model

    if 'apply' in request.POST:
        form = XlsDataSyncOptionForm(request.POST, model=model)
        if form.is_valid():
            filename = form.cleaned_data['filename']
            fields = form.cleaned_data['columns']
            out = six.BytesIO()
            with XlsTemplate(out) as xls:
                xls.process_model(model,
                                  fields=fields,
                                  queryset=queryset)
            out.seek(0)
            response = HttpResponse(out.read(),
                                    content_type="application/vnd.ms-excel"
                                    )
            response['Content-Disposition'] = six.b('attachment;filename="%s"' % filename)
            return response
    else:
        filename = '{}.xls'.format(model._meta.model_name)
        initial = {'_selected_action': request.POST.getlist(helpers.ACTION_CHECKBOX_NAME),
                   'select_across': request.POST.get('select_across') == '1',
                   'action': get_action(request),
                   'filename': filename}
        form = XlsDataSyncActionOptionForm(initial=initial, model=model)
    media = modeladmin.media + form.media
    ctx = {
        'form': form,
        'change': True,
        'action_short_description': _('Generate Excel Template'),
        'title': _('Generate Excel Template'),
        'is_popup': False,
        'action': _('Generate Template'),
        'opts': model._meta,
        'app_label': model._meta.app_label,
        'media': mark_safe(media)}
    ctx.update(modeladmin.admin_site.each_context(request))

    return render(request,
                  'excel_data_sync/options.html',
                  ctx)
