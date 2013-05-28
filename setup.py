# -*- coding: utf-8 -*-
"""
EngineAuth
==========


Quick links
-----------

- `User Guide <http://engineauth.appspot.com/>`_
- `Repository <http://github.com/scotch/engineauth>`_
- `Issue Tracker <https://github.com/scotch/engineauth/issues>`_
- `Wiki <https://github.com/scotch/engineauth/wiki>`_

"""
from setuptools import setup

setup(
    name = 'EngineAuth',
    version = '0.2.0',
    license = 'Apache Software License',
    url = 'http://engineauth.appspot.com',
    description = "Google App Engine: Multi-Provider Authentication Simplified.",
    long_description = __doc__,
    author = 'Kyle Finley',
    author_email = 'kyle.finley@gmail.com',
    zip_safe = False,
    platforms = 'any',
    py_modules = [
        'engineauth',
    ],
    packages = [
        'engineauth',
        'engineauth.strategies',
    ],
    include_package_data=True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)