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
The module plug-in providing the ```echo``` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
from collections import OrderedDict

from deployer.rendering import render
from deployer.result import Result

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Echo(Plugin):
    """Print data to console."""

    TAG = 'echo'

    def __init__(self, msg):
        """Ctor."""
        self.msg = msg['echo']

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Echo.TAG not in node:
            return False

        return True

    @staticmethod
    def build(node):
        """Build an `Echo` node."""
        yield Echo(node)

    def execute(self, context):
        """Perform the plugin's task purpose."""
        if context:
            msg = render(self.msg, **context.variables.last())
        else:
            msg = self.msg

        for line in msg.splitlines(False):
            LOGGER.info("| %s", line)

        return Result(result='success')
