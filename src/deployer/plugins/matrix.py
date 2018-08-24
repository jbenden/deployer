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

import logging
from collections import OrderedDict

from schema import And
from schema import Schema
from schema import SchemaError

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Matrix(Plugin):
    """Manage multiple combinations of a pipeline."""

    TAG = 'matrix'

    SCHEMA = {
        'tags': [And(str, len)],
        'tasks': [dict],
    }

    def __init__(self, node):
        """Ctor."""
        self._tags = node['tags']
        self._tasks = node['tasks']

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Matrix.TAG not in node:
            return False

        try:
            Schema(Matrix.SCHEMA).validate(node[Matrix.TAG])
        except SchemaError:
            return False

        for node in node[Matrix.TAG]['tasks']:
            if not Plugin._recursive_valid(node):
                return False

        return True

    @staticmethod
    def build(node):
        """Build a ```Matrix``` node."""
        yield Matrix(node[Matrix.TAG])

    def _execute_tasks(self, context):
        result = 'success'

        for node in self._tasks:
            for plugin in Plugin._recursive_build(node):
                result = plugin.execute(context)
                if not result == 'success':
                    break
            if not result == 'success':
                break

        return result

    def execute(self, context):
        """Perform the plugin's task purpose."""
        result = 'success'
        for tag in self._tags:
            LOGGER.debug('Beginning matrix entry: %s', tag)
            result = self._execute_tasks(context)
            LOGGER.debug('Completed matrix entry: %s', tag)
            if not result == 'success':
                break

        return result
