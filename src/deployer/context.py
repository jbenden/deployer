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
Data services and state management.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import os
import platform
import sys
from collections import deque


class Stack:  # noqa: no-cover
    """Stack data structure."""

    def __init__(self):  # noqa: no-cover
        """Ctor."""
        self.__storage = deque()

    def is_empty(self):  # noqa: no-cover
        """Determine if the stack is empty."""
        return len(self.__storage) == 0

    def push(self, p):  # noqa: no-cover
        """Add element to stack."""
        self.__storage.append(p)

    def pop(self):  # noqa: no-cover
        """Remove element from stack."""
        return self.__storage.pop()

    def last(self):  # noqa: no-cover
        """Return the right-most element on the stack."""
        return self.__storage[-1]

    def __len__(self):  # noqa: no-cover
        """Return the number of elements on the stack."""
        return len(self.__storage)

    def push_last(self):  # noqa: no-cover
        """Re-push the last item on to the stack."""
        self.__storage.append(self.last().copy())


class Context:
    """Data container for pipeline state."""

    variables = None

    def __init__(self):
        """Ctor."""
        # create our variable stack
        self.__class__.variables = Stack()

        # add the default set of templating variables.
        self.__class__.variables.push({
            'nbcpus': self.__class__.__detect_ncpus(),
            'node': platform.node(),
            'platform': sys.platform.lower(),
            'is_linux': sys.platform.lower().startswith('linux'),
            'is_bsd': sys.platform.lower().find('bsd') != -1,
            'is_darwin': sys.platform.lower().startswith('darwin'),
            'is_windows': sys.platform.lower().startswith('win'),
            'is_travis': 'TRAVIS' in os.environ,
            'is_appveyor': 'APPVEYOR' in os.environ,
            'is_ci': 'CI' in os.environ or 'CONTINUOUS_INTEGRATION' in os.environ,
        })

    @staticmethod
    def __detect_ncpus():  # noqa: no-cover
        """Detect the number of effective CPUs in the system."""
        # for Linux, Unix and MacOS
        if hasattr(os, "sysconf"):
            if "SC_NPROCESSORS_ONLN" in os.sysconf_names:
                # Linux and Unix
                ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
                if isinstance(ncpus, int) and ncpus > 0:
                    return ncpus
            else:
                # MacOS X
                return int(os.popen2("sysctl -n hw.ncpu")[1].read())  # nosec
        # for Windows
        if "NUMBER_OF_PROCESSORS" in os.environ:
            ncpus = int(os.environ["NUMBER_OF_PROCESSORS"])
            if ncpus > 0:
                return ncpus
        # return the default value
        return 1
