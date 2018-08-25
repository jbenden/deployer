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
The module providing the base class of all ```PyDeployer``` plug-ins.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging

from deployer.registry import Registry

from .plugin_proxy import PluginProxy

LOGGER = logging.getLogger(__name__)


class InvalidNode(RuntimeError):
    """Exception thrown when a YAML section cannot be handled via all plug-ins."""

    def __init__(self, node):
        """Ctor."""
        self.node = node

    def __str__(self):
        """Get a string representation of this exception."""
        return "All available plug-ins are unable to handle the '%r' expression." % self.node    # noqa: no-cover


class FailedValidation(RuntimeError):
    """Exception thrown when a YAML section cannot be correctly validated by a plug-in."""

    def __init__(self, node):
        """Ctor."""
        self.node = node

    def __str__(self):
        """Get a string representation of this exception."""
        return "Failed to validate expression:\n\n%r" % self.node                                # noqa: no-cover


class Plugin:
    """The base class of all ```PyDeployer``` plug-ins."""

    @staticmethod
    def _find_matching_plugin_for_node(node):
        """Locate a plug-in which handles the specified `node`; else returns `None`."""
        plugins = Registry().plugins()

        # print("Got the key %s" % node_key)
        for node_key in node.keys():
            for plugin in plugins:
                # print("Plug: %r" % plugin)
                if plugin in node_key:
                    return plugins[plugin]

        return None

    @staticmethod
    def _recursive_valid(node):
        # find a workable plugin
        plugin = Plugin._find_matching_plugin_for_node(node)
        if plugin:
            return plugin.valid(node)
        else:
            return False

    @staticmethod
    def _recursive_build(node):
        # find a workable plugin
        plugin = Plugin._find_matching_plugin_for_node(node)
        if plugin:
            if plugin.valid(node):
                # handle common elements
                name = node['name'] if 'name' in node else plugin.TAG
                when = node['when'] if 'when' in node else None
                for sub_node in plugin.build(node):
                    yield PluginProxy(name, sub_node, when=when)
            else:
                raise FailedValidation(node)
        else:
            raise InvalidNode(node)
