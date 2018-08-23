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
The module plug-in providing the ``env`` command.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import fnmatch
import logging
import os
from collections import OrderedDict

from schema import And
from schema import Optional
from schema import Or
from schema import Schema

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Env(Plugin):
    """Manage environment variables."""

    TAG = 'env'

    SCHEMA = {
        Optional('set'): {And(str, len): And(str, len)},
        Optional('unset'): And(len, Or(And(str, len), [And(str, len)])),
    }

    def __init__(self, node):
        """Ctor."""
        self.env_set = node['set'] if 'set' in node else {}

        if 'unset' in node:
            if type(node['unset']) not in (list,):
                self.env_unset = [node['unset']]
            else:
                self.env_unset = node['unset']
        else:
            self.env_unset = []

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Env.TAG not in node:
            return False

        return Schema(Env.SCHEMA).validate(node[Env.TAG])

    @staticmethod
    def build(node):
        """Build an Echo node."""
        if Env.valid(node):
            yield Env(node['env'])

    def execute(self):
        """Perform the plugin's task purpose."""
        for env in os.environ.copy():
            for pattern in self.env_unset:
                if fnmatch.fnmatchcase(env, pattern):
                    LOGGER.debug("Removing '%s' from system environment.", env)
                    try:
                        os.unsetenv(env)
                    except AttributeError:
                        pass
                    del os.environ[env]
                else:
                    LOGGER.debug("Keeping '%s' present in the system environment.", env)
        for key, value in self.env_set.items():
            LOGGER.debug("Setting '%s' to '%s', in the system environment.", key, value)
            os.putenv(key, value)
            os.environ[key] = value
