# -*- coding: utf-8 -*-
from django.apps import apps
from django.core.management.base import BaseCommand
# from excel_data_sync.inspector import process_model
from excel_data_sync.xls import XlsTemplate


class Command(BaseCommand):
    args = ''
    help = 'Help text here....'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('model', nargs='?', default=None)
        parser.add_argument('--data', action='store_true', default=False)
        parser.add_argument('-f',
                            '--filename', action='store', dest='filename',
                            default=None,
                            help="Filename",
                            )

    def handle(self, *args, **options):
        model = options['model']
        filename = options['filename']
        m = apps.get_model(model)
        f = filename or '{}.xls'.format(model)
        if options['data']:
            qs = m.objects.all()
        else:
            qs = None
        with XlsTemplate(f) as xls:
            xls.process_model(m, queryset=qs)
        self.stdout.write("Saved..{}".format(f))
        if qs:
            self.stdout.write("Dumped {} records".format(qs.count()))
