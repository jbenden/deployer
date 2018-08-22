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

# pylint: disable=C0111,R0903

"""
A central repository of global data.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

import six

from deployer.singleton import Singleton

LOGGER = logging.getLogger(__name__)


@six.add_metaclass(Singleton)
class Registry(object):
    """A central data repository. Responsible for alleviating global variable usage."""

    __metaclass__ = Singleton

    plugin_manager = None

    def __init__(self):
        """Ctor."""
        self._plugins = {}

    def plugins(self):
        """All available plugins."""
        return self._plugins

    def register_plugin(self, name, cls):
        """Register the `cls` for handling pipeline nodes, utilizing `name`."""
        LOGGER.debug('Registering %s, with class %s, as a plug-in.', name, cls.__name__)
        self._plugins.update([(name, cls)])
