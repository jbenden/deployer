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

from .plugin import Plugin
from .plugin_proxy import PluginProxy

LOGGER = logging.getLogger(__name__)


class TopLevel(Plugin):
    """The very top most object of a whole pipeline."""

    @staticmethod
    def valid(node):
        """Ensure the top-level node structure is valid."""
        if type(node) is not list:
            return False

        return True

    @staticmethod
    def build(document):
        """Produce an iterable AST representation of a YAML pipeline definition."""
        if TopLevel.valid(document):
            for node in document:
                # find a workable plugin
                plugin = Plugin._find_matching_plugin_for_node(node)
                if plugin:
                    if plugin.valid(node):
                        for sub_node in plugin.build(node):
                            yield PluginProxy(sub_node)
                    else:
                        raise RuntimeError("Failed validation: %r" % node)
                else:
                    raise RuntimeError("Could not handle node: %r" % node)
