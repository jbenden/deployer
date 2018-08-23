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

"""Namespace for all built-in plugins shipped with ```PyDeployer```."""

# flake8: noqa

from .api import hookimpl
from .echo import Echo
from .env import Env
from .top_level import TopLevel


@hookimpl
def deployer_register(registry):
    """Perform built-in plug-in registrations."""
    registry.register_plugin('echo', Echo)
    registry.register_plugin('env', Env)
