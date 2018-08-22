========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |coveralls|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/py-deployer/badge/?style=flat
    :target: https://readthedocs.org/projects/py-deployer
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/jbenden/deployer.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/jbenden/deployer

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/jbenden/deployer?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/jbenden/deployer

.. |requires| image:: https://requires.io/github/jbenden/deployer/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/jbenden/deployer/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/jbenden/deployer/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/github/jbenden/deployer

.. |version| image:: https://img.shields.io/pypi/v/py-deployer.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/py-deployer

.. |commits-since| image:: https://img.shields.io/github/commits-since/jbenden/deployer/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/jbenden/deployer/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/py-deployer.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/py-deployer

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/py-deployer.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/py-deployer

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/py-deployer.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/py-deployer


.. end-badges

Local+CI+CD Made Easy!

* Free software: Apache Software License 2.0

Installation
============

::

    pip install deployer

Documentation
=============

https://py-deployer.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
