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
A module holding the results of all plug-ins.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""


class Result(dict):
    """Represents the resultant of a plug-in's execution."""

    def __bool__(self):
        """Cast to boolean."""
        return self['result'] != 'failure'

    def __nonzero__(self):
        """Cast to boolean."""
        return self.__bool__()  # noqa: no-cover

    def __str__(self):
        """Return our `stdout` if present, otherwise returns the `result` value."""
        return self['stdout'] if 'stdout' in self else str(self['result'])

    def failed(self):
        """Determine if the resultant is a failure."""
        return self['result'] == 'failure'  # noqa: no-cover

    def succeeded(self):
        """Determine if the resultant is a success."""
        return self['result'] != 'failure'  # noqa: no-cover

    def skipped(self):
        """Determine if the resultant was skipped."""
        return self['result'] == 'skipped'  # noqa: no-cover
