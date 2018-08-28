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
A module providing a base class of all ```PyDeployer``` plug-ins, which require support for processing nested tasks.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging

from schema import Schema
from schema import SchemaError

from deployer.util import merge_dicts

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class PluginWithTasks(Plugin):
    """A ```PyDeployer``` plug-in base that offers supporting sub-tasks."""

    BASE_SCHEMA = {
        'tasks': [object],
    }

    def __init__(self, node):
        """Ctor."""
        self._tasks = node['tasks']

    @staticmethod
    def _valid(schema, tag, node):
        try:
            Schema(merge_dicts(schema, PluginWithTasks.BASE_SCHEMA)).validate(node[tag])
        except SchemaError:
            return False

        for node in node[tag]['tasks']:
            if not Plugin._recursive_valid(node):
                return False

        return True

    def _execute_tasks(self, context):
        result = 'success'

        for node in self._tasks:
            for plugin in Plugin._recursive_build(node, inherited_tags=self._match_tags):
                result = plugin.execute(context)
                if result == 'failure':
                    break
            if result == 'failure':
                break

        return result
