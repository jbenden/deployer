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

from deployer.registry import Registry


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
