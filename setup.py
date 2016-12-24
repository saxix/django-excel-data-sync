#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(*files):
    content = ''
    for f in files:
        content += codecs.open(os.path.join(ROOT, 'src',
                                            'requirements', f), 'r').read()
    return content


def get_version(*file_paths):
    """Retrieves the version from excel_data_sync/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("src", "excel_data_sync", "__init__.py")

ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__)))
reqs = 'install.py%d.pip' % sys.version_info[0]

install_requires = read('install.pip'),
tests_requires = read('testing.pip')
dev_requires = tests_requires + read('develop.pip')

if sys.argv[-1] == 'publish':
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-excel-data-sync',
    version=version,
    description="""Creates XLS sheets to upload data into django models""",
    long_description=readme + '\n\n' + history,
    author='Stefano Apostolico',
    author_email='s.apostolico@gmail.com',
    url='https://github.com/saxix/dj-excel-data-sync',
    package_dir={'': 'src'},
    packages=['excel_data_sync'],
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'django': ["django>=1.8,<=1.10"],
        'dev': dev_requires,
        'test': tests_requires,
        'admin': ['admin-extra-urls']
    },
    license="MIT",
    zip_safe=False,
    keywords='django excel',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
