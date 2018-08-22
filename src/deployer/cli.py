# -*- coding: utf-8 -*-
# Copyright 2018 Joseph Benden <joe@benden.us>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mdeployer` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``deployer.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``deployer.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import logging
import os
import sys

import click

try:
    import colorama
    colorama.init(strip=True)
except ImportError:
    pass

try:
    import colorlog
except ImportError:
    pass


def setup_logging():
    """Initialize the logging infrastructure."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    format = '%(asctime)s - %(levelname)-8s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    if 'colorlog' in sys.modules and os.isatty(2):
        cformat = '%(log_color)s' + format
        f = colorlog.ColoredFormatter(cformat, date_format,
                                      log_colors={'DEBUG': 'reset', 'INFO': 'reset',
                                                  'WARNING': 'bold_yellow', 'ERROR': 'bold_red',
                                                  'CRITICAL': 'bold_red'})
    else:
        f = logging.Formatter(format, date_format)
    ch = logging.StreamHandler()
    ch.setFormatter(f)
    root.addHandler(ch)


LOGGER = logging.getLogger(__name__)


@click.command()
@click.argument('names', nargs=-1)
def main(names):
    """Entry point."""
    setup_logging()
    click.echo(repr(names))
