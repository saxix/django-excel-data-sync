# -*- coding: utf-8 -*-
from django.contrib.staticfiles.management.commands.runserver import \
    Command as RunServer
from django.core.management import call_command

from example.management.demo import create_admin, create_sample_data
from example.models import DemoModel


class Command(RunServer):
    args = ''
    help = 'Help text here....'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--admin', action='store_true', dest='admin',
            help='create/reset administrator (admin/123)'
        )
        parser.add_argument(
            '--zap', action='store_true', dest='zap',
            help='empty database'
        )
        parser.add_argument('--data',
                            dest='data',
                            const=10,
                            # default=10,
                            action='store',
                            nargs='?',
                            type=int,
                            help='creates sample data. Default 10 rows')

    def handle(self, *args, **options):
        call_command('migrate')
        if options['admin']:
            create_admin()
        if options['zap']:
            DemoModel.objects.all().delete()
        if options['data']:
            create_sample_data(options['data'])

        super(Command, self).handle(*args, **options)
