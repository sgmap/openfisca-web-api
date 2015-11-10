#! /usr/bin/env python
# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages


setup(
    name = 'OpenFisca-Web-API',
    version = '0.5.2.dev0',

    author = 'OpenFisca Team',
    author_email = 'contact@openfisca.fr',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        ],
    description = u'Web API for OpenFisca',
    keywords = 'api benefit microsimulation server social tax web',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    url = 'https://github.com/openfisca/openfisca-web-api',

    data_files = [
        ('share/locale/fr/LC_MESSAGES', ['openfisca_web_api/i18n/fr/LC_MESSAGES/openfisca-web-api.mo']),
        (
            'share/openfisca/openfisca-web-api', [
                'CHANGELOG.md',
                'development-france.ini',
                'development-tunisia.ini',
                'LICENSE',
                'README.md',
                'test.ini',
                ],
            ),
        ],
    entry_points = {
        'paste.app_factory': 'main = openfisca_web_api.application:make_app',
        },
    extras_require = {
        'dev': [
            'PasteScript',
            ],
        'france': [
            'OpenFisca-France >= 0.5.1',
            ],
        'test': [
            'nose',
            ],
        },
    install_requires = [
        'Babel >= 0.9.4',
        'Biryani >= 0.10.4',
        'OpenFisca-Core >= 0.5.0',
        'OpenFisca-Parsers >= 0.5',
        'PasteDeploy',
        'WebError >= 0.10',
        'WebOb >= 1.1',
        ],
    message_extractors = {'openfisca_web_api': [
        ('**.py', 'python', None),
        ]},
    packages = find_packages(exclude=['openfisca_web_api.tests*']),
    test_suite = 'nose.collector',
    )
