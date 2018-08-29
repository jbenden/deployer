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
The module plug-in providing the ```set``` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
from collections import OrderedDict

from schema import And
from schema import Schema
from schema import SchemaError

from deployer.result import Result

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Set(Plugin):
    """Manage template variables."""

    TAG = 'set'

    SCHEMA = {And(str, len): And(object)}

    def __init__(self, node):
        """Ctor."""
        self.variables = node

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Set.TAG not in node:
            return False

        try:
            Schema(Set.SCHEMA).validate(node[Set.TAG])
        except SchemaError:
            return False

        return True

    @staticmethod
    def build(node):
        """Build a Set node."""
        yield Set(node[Set.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        if not context:  # noqa: no-cover
            raise RuntimeError("The set plug-in requires a context to function correctly")

        for key, value in self.variables.items():
            LOGGER.debug("Setting '%s' to '%s', in the templating environment.", key, value)
            context.variables.last()[key] = value
        return Result(result='success')
