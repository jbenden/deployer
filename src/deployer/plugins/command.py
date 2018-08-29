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
The module plug-in providing the ```command``` command.

Accepts a string and parses as a POSIX shell would, to produce the
complete `ARGV` array that is then directly executed using either
`execvpe` or `CreateProcess` (using Twisted's support for
spawning programs).

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
import shlex
from collections import OrderedDict

from schema import And
from schema import Schema
from schema import SchemaError
from twisted.internet.error import ProcessTerminated

from deployer.rendering import render
from deployer.result import Result

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Command(Plugin):
    """Run programs (without indirection via a shell)."""

    TAG = 'command'

    SCHEMA = And(str, len)

    def __init__(self, node):
        """Ctor."""
        self.cmd = node

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Command.TAG not in node:
            return False

        try:
            Schema(Command.SCHEMA).validate(node[Command.TAG])
        except SchemaError:
            return False

        return True

    @staticmethod
    def build(node):
        """Build a ```Command``` node."""
        yield Command(node[Command.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        result = Result(result='success')

        cmd = render(self.cmd, **context.variables.last())
        argv = shlex.split(cmd, False, False)
        LOGGER.debug("Running: %r" % argv)

        try:
            Plugin.run(argv)
        except ProcessTerminated as e:
            LOGGER.error("Process failed and returned %d" % e.exitCode)
            result = Result(result='failure')

        return result
