# Copyright 2026 UWIT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/status_dashboard>`_.
"""

url = "https://github.com/uw-it-aca/status_dashboard"
setup(
    name='status_dashboard',
    packages=['status_dashboard'],
    author="UWIT Student & Educational Technology Services",
    author_email="aca-it@uw.edu",
    install_requires=[
        'tornado>=6,<7',
        'pyyaml',
        'jinja2',
        'prometheus-api-client',
        'prometheus-client',
    ],
    license='Apache License, Version 2.0',
    description='status dashboard reflecting prometheus metrics',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.12',
    ],
)
