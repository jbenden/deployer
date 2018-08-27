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
The module plug-in providing the ```shell``` command.

Accepts a string, or string block, and filters it through the
templating engine, saving it to a temporary file. This
temporary file is then executed using the specified
`executable`, or the default executable.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import logging
import sys
from collections import OrderedDict

from schema import And
from schema import Optional
from schema import Schema
from schema import SchemaError
from twisted.internet.error import ProcessTerminated

from deployer.rendering import render
from deployer.third_party.temp import NamedTemporaryFile

from .plugin import Plugin

LOGGER = logging.getLogger(__name__)


class Shell(Plugin):
    """Run shell scripts."""

    TAG = 'shell'

    SCHEMA = {
        Optional('executable'): And(str, len),
        Optional('executable_flags'): [And(str, len)],
        'script': And(str, len),
    }

    STANDARD_EXECUTABLES = {
        "sh": {
            "executable": "/bin/sh",
            "flags": ["-euf"],
            "extension": ".sh",
        },
        "bash": {
            "executable": "/bin/bash",
            "flags": ["-euf", "-o", "pipefail"],
            "extension": ".sh",
        },
        "cmd": {
            "executable": "\\Windows\\System32\\cmd.exe",
            "flags": ["/q", "/c"],
            "extension": ".bat",
        },
        "powershell": {
            "executable": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
            "flags": ["-Version", "4.0", "-NoLogo", "-NonInteractive", "-WindowStyle", "Hidden", "-File"],
            "extension": ".ps1",
        },
    }

    def __init__(self, node):
        """Ctor."""
        default = 'cmd' if sys.platform.lower().startswith('win') else 'sh'
        executable = node['executable'] if 'executable' in node else default
        if executable not in self.STANDARD_EXECUTABLES:
            self._executable = executable
            self._flags = node['executable_flags'] if 'executable_flags' in node else []
            self._extension = ''
        else:
            self._executable = self.STANDARD_EXECUTABLES[executable]['executable']
            self._flags = node['executable_flags'] if 'executable_flags' in node else \
                self.STANDARD_EXECUTABLES[executable]['flags']
            self._extension = self.STANDARD_EXECUTABLES[executable]['extension']

        self._script = node['script']

    @staticmethod
    def valid(node):
        """Ensure node structure is valid."""
        if type(node) is not OrderedDict:
            return False

        if Shell.TAG not in node:
            return False

        try:
            Schema(Shell.SCHEMA).validate(node[Shell.TAG])
        except SchemaError:
            return False

        return True

    @staticmethod
    def build(node):
        """Build a ```Shell``` node."""
        yield Shell(node[Shell.TAG])

    def execute(self, context):
        """Perform the plugin's task purpose."""
        result = 'success'

        cmd = render(self._script, **context.variables.last())

        with NamedTemporaryFile('w+t', suffix=self._extension) as f:
            f.write(cmd)
            f.flush()

            LOGGER.debug("Running: %r" % f.name)

            try:
                Plugin.run([self._executable] + self._flags + [f.name])
            except ProcessTerminated as e:
                LOGGER.error("Process failed and returned %d" % e.exitCode)
                result = 'failure'

        return result
