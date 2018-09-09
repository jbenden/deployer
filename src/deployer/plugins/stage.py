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
The module plug-in providing the ```stage``` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import contextlib
import logging
from collections import OrderedDict

from schema import And
from schema import Optional

from deployer.plugins.plugin_with_tasks import PluginWithTasks
from deployer.result import Result

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def scoped_variables(context, scope):
    """Ensure all variables introduced by a plug-in are scoped to itself."""
    if context and scope:
        context.variables.push_last()
    try:
        yield
    finally:
        if context and scope:
            context.variables.pop()


class Stage(PluginWithTasks):
    """Manage a grouping of tasks within a pipeline."""

    TAG = 'stage'

    SCHEMA = {
        Optional('scope'): And(bool),
    }

    def __init__(self, node):
        """Ctor."""
        super(Stage, self).__init__(node)
        self._scope = node['scope'] if 'scope' in node else True

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Stage.TAG not in node:
            return False

        return PluginWithTasks._valid(Stage.SCHEMA, Stage.TAG, node)

    @staticmethod
    def build(node):
        """Build a ```Stage``` node."""
        yield Stage(node[Stage.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        with scoped_variables(context, self._scope):
            LOGGER.debug('Beginning stage%s' % (' (with scope)' if self._scope else ''))
            result = self._execute_tasks(context)
            LOGGER.debug('Completed stage')

        if result['result'] in ['skipped', 'continue']:
            result = Result(result='success')

        return result
