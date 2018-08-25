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
A module offering services during a plug-in's life-time.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import contextlib
import logging
import time

from deployer.proxy import Proxy
from deployer.rendering import BooleanExpression

LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def with_scoped_variables(context, item):
    """Ensure all variables introduced by the ```Matrix``` plug-in are scoped to itself."""
    if context and item is not None:
        context.variables.push_last()

        # set the current loop item variable
        context.variables.last()['item'] = item
    try:
        yield
    finally:
        if context and item is not None:
            context.variables.pop()


class PluginProxy(Proxy):
    """Wrap-around for all plug-ins."""

    def __init__(self, name, obj, when=None, with_items=None):
        """Ctor."""
        super(PluginProxy, self).__init__(obj)
        self._name = name
        self._when = when
        self._with_items = with_items

    def _execute_one(self, context):
        LOGGER.info("%s is starting.", self._name)
        # emit a start event here, events MUST have correlation id
        start = time.time()
        result = object.__getattribute__(self, "_obj").execute(context)
        end = time.time()
        LOGGER.info("%s has finished with %r, in %0.9f seconds.", self._name, result, (end - start))
        # emit an end event here
        return result

    def execute(self, context):
        """Proxy of a plug-in's `execute` method."""
        result = 'failed'

        if self._when is not None:
            expr = BooleanExpression(self._when)

            if not expr.evaluate(context):
                return 'skipped'

        if self._with_items is not None:
            for item in self._with_items:
                with with_scoped_variables(context, item):
                    result = self._execute_one(context)
                    if result == 'failure':
                        break
        else:
            result = self._execute_one(context)

        return result
