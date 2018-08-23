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
The public plug-in API of the ``PyDeployer`` project.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pluggy

#: All ``PyDeployer`` plug-ins *MUST* decorate their hooks with `hookimpl`.
#: This decorator is used by :py:mod:`pluggy` to automatically find all
#: functions which implement a hook, per the available hooks specified
#: inside of :py:mod:`deployer.plugins.hookspec`.
hookimpl = pluggy.HookimplMarker("deployer")     # pylint: disable=invalid-name
