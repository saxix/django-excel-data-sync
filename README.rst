====================
Django ExcelDataSync
====================

.. image:: https://badge.fury.io/py/excel_data_sync.png
    :target: https://badge.fury.io/py/excel_data_sync

.. image:: https://travis-ci.org/saxix/django-excel-data-sync.png?branch=develop
    :target: https://travis-ci.org/saxix/django-excel-data-sync


It allows to create XLS file to import data into Django Model.
The xls implements most of the validation rules of the django model fields, this
prevent errors due the lack of constraints


Supported Fields
----------------

    - :py:class:`~django.db.models.BigIntegerField`
    - :py:class:`~django.db.models.BooleanField`
    - :py:class:`~django.db.models.AutoField`
    - :py:class:`~django.db.models.CharField`
    - :py:class:`~django.db.models.DateField`
    - :py:class:`~django.db.models.DateTimeField`
    - :py:class:`~django.db.models.DecimalField`
    - :py:class:`~django.db.models.EmailField`
    - :py:class:`~django.db.models.FloatField`
    - :py:class:`~django.db.models.ForeignKey`
    - :py:class:`~django.db.models.GenericIPAddressField`
    - :py:class:`~django.db.models.IntegerField`
    - :py:class:`~django.db.models.NullBooleanField`
    - :py:class:`~django.db.models.PositiveIntegerField`
    - :py:class:`~django.db.models.SmallIntegerField`
    - :py:class:`~django.db.models.TextField`
    - :py:class:`~django.db.models.TimeField`
    - :py:class:`~django.db.models.URLField`
    - :py:class:`~django.db.models.UUIDField`
`

Supported Validations
---------------------

Fields attributes
~~~~~~~~~~~~~~~~~

    - choices :py:attr:`django.db.models.Field.choices`
    - unique :py:attr:`django.db.models.Field.unique`


Field Validators
~~~~~~~~~~~~~~~~


    - max value (:class:`django.core.validators.MaxValueValidator`)
    - min value (:class:`django.core.validators.MinValueValidator`)
    - max length (:class:`django.core.validators.MaxLengthValidator`)
    - min length (:class:`django.core.validators.MinLengthValidator`)


Documentation
-------------

The full documentation is at http://django-excel-data-sync.readthedocs.io/en/latest/

Quickstart
----------

Install ExcelDataSync::

    pip install django-excel-data-sync

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'excel_data_sync.apps.XlsDataSyncConfig',
        ...
    )


Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

