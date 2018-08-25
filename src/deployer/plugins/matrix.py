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
The module plug-in providing the ``matrix`` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import contextlib
import logging
from collections import OrderedDict

from schema import And

from deployer.plugins.plugin_with_tasks import PluginWithTasks

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def matrix_scoped_variables(context, tag):
    """Ensure all variables introduced by the ```Matrix``` plug-in are scoped to itself."""
    if context:
        context.variables.push_last()

        # set the current matrix tag variable
        context.variables.last()['matrix_tag'] = tag

        # append the current matrix tag onto the descending list of entered matrices.
        if 'matrix_list' not in context.variables.last():
            context.variables.last()['matrix_list'] = []
        context.variables.last()['matrix_list'].append(tag)
    try:
        yield
    finally:
        if context:
            context.variables.pop()


class Matrix(PluginWithTasks):
    """Manage multiple combinations of a pipeline."""

    TAG = 'matrix'

    SCHEMA = {
        'tags': [And(str, len)],
    }

    def __init__(self, node):
        """Ctor."""
        self._tags = node['tags']
        super(Matrix, self).__init__(node)

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Matrix.TAG not in node:
            return False

        return PluginWithTasks._valid(Matrix.SCHEMA, Matrix.TAG, node)

    @staticmethod
    def build(node):
        """Build a ```Matrix``` node."""
        yield Matrix(node[Matrix.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        result = 'success'

        for tag in self._tags:
            with matrix_scoped_variables(context, tag):
                LOGGER.debug('Beginning matrix entry: %s', tag)
                result = self._execute_tasks(context)
                LOGGER.debug('Completed matrix entry: %s', tag)
            if not result == 'success':
                break

        return result
