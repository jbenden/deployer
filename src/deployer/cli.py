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
import platform
import sys

import click
import pluggy
import six

from deployer import __version__
from deployer import plugins as builtin_plugins
from deployer.context import Context
from deployer.loader import ordered_load
from deployer.plugins import hookspec as hookspecs
from deployer.plugins.top_level import TopLevel
from deployer.registry import Registry
from deployer.util import start_reactor
from deployer.util import stop_reactor

try:
    import colorama                                            # noqa: no-cover
    colorama.init(strip=True)                                  # noqa: no-cover
except ImportError:                                            # noqa: no-cover
    pass                                                       # noqa: no-cover

try:
    import colorlog                                            # noqa: no-cover
except ImportError:                                            # noqa: no-cover
    pass                                                       # noqa: no-cover


def setup_logging(level=logging.DEBUG):  # noqa: no-cover
    """Initialize the logging infrastructure."""
    root = logging.getLogger()
    root.setLevel(level)
    format = '%(asctime)s.%(msecs)03d - %(levelname)-8s - %(message)s'
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
    while root.handlers:
        root.handlers.pop()
    root.addHandler(ch)


def _get_plugin_manager(plugins=()):  # noqa: no-cover
    pm = pluggy.PluginManager('deployer')
    pm.add_hookspecs(hookspecs)
    pm.register(sys.modules[__name__])
    pm.register(builtin_plugins)
    pm.load_setuptools_entrypoints('py-deployer')
    for plugin in plugins:
        if isinstance(plugin, six.string_types):
            __import__(plugin)
            try:
                pm.register(sys.modules[plugin])
            except KeyError:
                print('The %s plugin was requested to load and register; but failed to import!' % plugin)
                sys.exit(1)
        else:
            pm.register(plugin)
    pm.check_pending()

    return pm


LOGGER = logging.getLogger(__name__)
THE_REACTOR = None


def initialize(level=logging.DEBUG):
    """Perform basic initialization of program."""
    global THE_REACTOR

    setup_logging(level)
    Registry.plugin_manager = _get_plugin_manager()
    Registry.plugin_manager.hook.deployer_register(registry=Registry())

    # start the twisted reactor
    if THE_REACTOR is None:
        THE_REACTOR = start_reactor()

        import atexit
        atexit.register(stop_reactor, THE_REACTOR)


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--debug', '-d', is_flag=True, default=False,
              help="Enable debugging and verbose output.")
@click.option('--silent', '-d', is_flag=True, default=False,
              help="Show minimal output; namely errors and fatal messages.")
def main(ctx, debug, silent):
    """Entry point."""
    # determine logging level
    level = logging.INFO
    if debug:
        level = logging.DEBUG
    if silent:
        level = logging.ERROR
    initialize(level)

    # print banner information
    LOGGER.info("Starting PyDeployer version %s" % __version__)
    LOGGER.info("(C) 2018 Joseph Benden <joe (at) benden.us>")
    LOGGER.info("Homepage: https://github.com/jbenden/deployer")

    # print basic system information
    LOGGER.info("Running with Python %s", sys.version.replace("\n", ""))
    LOGGER.info("Running on platform %s", platform.platform())

    if ctx.invoked_subcommand is None:
        sys.exit(0)


@main.command('exec')
@click.option('--tag', '-t', default=[], type=click.STRING, multiple=True, envvar='DEPLOYER_TAG',
              help="Only run tasks having these tags annotated (May be specified more than once.)")
@click.option('--matrix-tags', '-m', default='', type=click.STRING, envvar='DEPLOYER_MATRIX_TAGS',
              help="Only run the tasks within a matrix; if the fnmatch-style pattern succeeds "
                   "(Should be a comma-separated, fnmatch-style pattern.)")
@click.argument('pipeline', nargs=-1, type=click.File('rb'), required=True, metavar='<path/to/pipeline.yaml>')
def execute(tag, matrix_tags, pipeline):
    """Execute a pipeline definition."""
    for f in pipeline:
        LOGGER.info("Processing pipeline definition '%s'", f.name)

        try:
            document = ordered_load(f)
        except Exception as e:  # noqa: E722
            LOGGER.exception("Failed validation", e)
            document = None

        if TopLevel.valid(document):
            nodes = TopLevel.build(document)

            context = Context()
            context.tags = tag
            if isinstance(matrix_tags, six.string_types):
                context.matrix_tags = [i.strip() for i in matrix_tags.split(',') if i != '']
            else:  # noqa: no-cover
                LOGGER.critical("Matrix tags must be a string.")
                sys.exit(3)

            for node in nodes:
                result = node.execute(context)

                if not result:
                    sys.exit(1)
        else:
            sys.exit(2)


@main.command()
@click.argument('pipeline', nargs=-1, type=click.File('rb'), required=True, metavar='<path/to/pipeline.yaml>')
def validate(pipeline):
    """Validate a pipeline definition for syntactic correctness."""
    for f in pipeline:
        LOGGER.info("Processing pipeline definition '%s'", f.name)

        try:
            document = ordered_load(f)
        except:  # noqa: E722
            document = None

        if TopLevel.valid(document):
            click.secho('Document is OK.', fg='green')
        else:
            click.secho('Document is BAD.', fg='red')
            sys.exit(1)
