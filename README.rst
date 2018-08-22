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

.. end-badges

Local+CI+CD Made Easy!

* Free software: Apache Software License 2.0

Installation
============

::

    pip install deployer

Documentation
=============

https://py-deployer.readthedocs.io/en/latest/

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
