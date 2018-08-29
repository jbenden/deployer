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

"""Namespace for all built-in plugins shipped with ```PyDeployer```."""

# flake8: noqa

import logging
from collections import OrderedDict

from deployer.result import Result

from .api import hookimpl
from .command import Command
from .echo import Echo
from .env import Env
from .matrix import Matrix
from .plugin import Plugin
from .set import Set
from .shell import Shell
from .stage import Stage
from .top_level import TopLevel

LOGGER = logging.getLogger(__name__)


class Fail(Plugin):
    """Fail with purpose."""

    TAG = 'fail'

    def __init__(self, msg):
        """Ctor."""
        self.fail = msg['fail'] if 'fail' in msg else ''

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Fail.TAG not in node:
            return False

        return True

    @staticmethod
    def build(node):
        """Build a ```Fail``` node."""
        yield Fail(node)

    def execute(self, context):
        """Perform the plugin's task purpose."""
        if context:
            from deployer.rendering import render
            msg = render(self.fail, **context.variables.last())
        else:
            msg = self.fail
        LOGGER.error("| %s", msg)
        return Result(result='failure')


@hookimpl
def deployer_register(registry):
    """Perform built-in plug-in registrations."""
    registry.register_plugin('command', Command)
    registry.register_plugin('echo', Echo)
    registry.register_plugin('env', Env)
    registry.register_plugin('fail', Fail)
    registry.register_plugin('matrix', Matrix)
    registry.register_plugin('set', Set)
    registry.register_plugin('shell', Shell)
    registry.register_plugin('stage', Stage)
