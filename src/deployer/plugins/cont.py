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
The module plug-in providing the ```continue``` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
from collections import OrderedDict

from schema import And
from schema import Or
from schema import Schema
from schema import SchemaError

from deployer.rendering import BooleanExpression
from deployer.result import Result

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Continue(Plugin):
    """Determine if a scoping continues onwards executing."""

    TAG = 'continue'

    SCHEMA = {
        'when': [Or(And(bool), And(str, len))],
    }

    def __init__(self, node):
        """Ctor."""
        self._conditions = node['when'] if 'when' in node else []

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Continue.TAG not in node:
            return False

        try:
            Schema(Continue.SCHEMA).validate(node[Continue.TAG])
        except SchemaError:
            return False

        return True

    @staticmethod
    def build(node):
        """Build a `Continue` node."""
        yield Continue(node[Continue.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        for condition in self._conditions:
            expr = BooleanExpression(condition)

            if expr.evaluate(context):
                return Result(result='continue')

        return Result(result='success')
