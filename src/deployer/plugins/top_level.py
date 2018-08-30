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
The top-level object, representing an entire ```PyDeployer``` pipeline.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
import time

from deployer.result import Result

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class TopLevel(Plugin):
    """The very top most object of a whole pipeline."""

    def __init__(self, document):
        """Constructor."""
        self._document = document

    @staticmethod
    def valid(document):
        """Ensure the top-level node structure is valid."""
        if type(document) is not list:
            return False

        for node in document:
            if not Plugin._recursive_valid(node):
                return False

        return True

    @staticmethod
    def build(document):
        """Produce an iterable AST representation of a YAML pipeline definition."""
        yield TopLevel(document)

    def execute(self, context):
        """Perform the plugin's task purpose."""
        result = Result(result='success')

        LOGGER.info("Starting pipeline execution.")
        start = time.time()

        for node in self._document:
            for plugin in Plugin._recursive_build(node):
                result = plugin.execute(context)
                if not result:
                    break

        end = time.time()
        LOGGER.info("Finished pipeline execution in %0.9f seconds.", (end - start))

        return result
