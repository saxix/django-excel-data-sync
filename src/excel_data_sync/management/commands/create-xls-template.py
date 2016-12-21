# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.apps import apps

from excel_data_sync.inspector import process_model


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

        process_model(m, f, data=options['data'])
        self.stdout.write("Saved..{}".format(f))
