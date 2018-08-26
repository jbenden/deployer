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
A module providing support functionality.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import errno
import logging
import sys
from io import BytesIO

from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.error import ProcessDone
from twisted.internet.error import ProcessTerminated
from twisted.internet.error import ReactorNotRunning
from twisted.internet.protocol import ProcessProtocol
from twisted.python.failure import Failure

IS_WINDOWS = sys.platform.lower().startswith('win')
LOGGER = logging.getLogger(__name__)


def merge_dicts(*dict_args):
    """Merge dictionaries.

    Given any number of dicts, shallow copy and merge into a new dict.

    Precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class LoggingSubprocessProtocol(ProcessProtocol):
    """Simple Twisted protocol which logs a process'es output."""

    outBuf = ''
    errBuf = ''

    def connectionMade(self):
        """Triggered upon program start, as it is entering its' `main` function."""
        self.d = Deferred()

    def outReceived(self, data):
        """Triggered upon program `stdout` data arriving."""
        text = data.decode('utf-8')
        self.outBuf += text

        pos = self.outBuf.find("\n")
        while pos >= 0:
            LOGGER.info("| %s" % self.outBuf[:pos])
            self.outBuf = self.outBuf[pos + 1:len(self.outBuf)]
            pos = self.outBuf.find("\n")

    def errReceived(self, data):
        """Triggered upon program `stderr` data arriving."""
        text = data.decode('utf-8')
        self.errBuf += text

        pos = self.errBuf.find("\n")
        while pos >= 0:
            LOGGER.error("! %s" % self.errBuf[:pos])
            self.errBuf = self.errBuf[pos + 1:len(self.errBuf)]
            pos = self.errBuf.find("\n")

    def processEnded(self, reason):
        """Triggered upon the end of a program's execution."""
        if len(self.outBuf):
            LOGGER.info("| %s" % self.outBuf)

        if len(self.errBuf):
            LOGGER.error("! %s" % self.errBuf)

        if reason.check(ProcessDone):
            self.d.callback(self.outBuf)
        else:
            self.d.errback(reason)


class SubprocessProtocol(ProcessProtocol):
    """Simple Twisted protocol which captures a process'es standard output."""

    def connectionMade(self):
        """Triggered upon program start, as it is entering its' `main` function."""
        self.d = Deferred()
        self.outBuf = BytesIO()
        self.errBuf = BytesIO()
        self.outReceived = self.outBuf.write
        self.errReceived = self.errBuf.write

    def processEnded(self, reason):
        """Triggered upon the end of a program's execution."""
        out = self.outBuf.getvalue()
        err = self.errBuf.getvalue()
        if reason.check(ProcessDone):
            self.d.callback(out)
        else:
            LOGGER.error(err)
            self.d.errback(reason)


def async_check_output(args, reactor_process=None):
    """Execute and capture a process'es standard output, using ```Twisted```.

    :type args: list of str
    :type reactor_process: :class: twisted.internet.interfaces.IReactorProcess
    :rtype: Deferred
    """
    if reactor_process is None:                # noqa: no-cover
        from twisted.internet import reactor   # noqa: no-cover
        reactor_process = reactor              # noqa: no-cover

    process_protocol = SubprocessProtocol()
    try:
        reactor_process.spawnProcess(process_protocol, args[0], args)
        return process_protocol.d
    except OSError as e:
        if e.errno is None or e.errno == errno.ENOENT:
            return defer.fail(ProcessTerminated(exitCode=1))
        else:
            return defer.fail(e)


def sync_check_output(argv=(), reactor_process=None):
    """Execute and capture a process'es standard output."""
    if reactor_process is None:                # noqa: no-cover
        from twisted.internet import reactor   # noqa: no-cover
        reactor_process = reactor              # noqa: no-cover

    import threading

    event = threading.Event()
    output = [None]

    def _cb(result):
        output[0] = result.decode('utf-8').rstrip("\r\n")
        event.set()

    def _cbe(result):
        output[0] = result
        event.set()

    def _main(args):
        d = async_check_output(args)
        d.addCallback(_cb)
        d.addErrback(_cbe)

    reactor_process.callFromThread(_main, argv)

    event.wait(None)

    if isinstance(output[0], Failure):
        output[0].raiseException()

    return output[0]


def start_reactor():
    """Start a ```Twisted``` reactor, in a background thread."""
    from twisted.internet import reactor as _reactor
    import threading

    event = threading.Event()

    def _start():
        event.set()
        _reactor.run(installSignalHandlers=0)

    import threading
    t = threading.Thread(target=_start, group=None)
    t.daemon = True
    t.start()

    event.wait(None)

    if not IS_WINDOWS:              # noqa: no-cover
        _reactor._handleSignals()   # noqa: no-cover

    return _reactor


def stop_reactor(the_reactor):
    """Stop a running ```Twisted``` reactor."""
    def stop(result, stopReactor):
        if stopReactor:                # noqa: no-cover
            try:                       # noqa: no-cover
                the_reactor.stop()     # noqa: no-cover
            except ReactorNotRunning:  # noqa: no-cover
                pass                   # noqa: no-cover

    the_reactor.callWhenRunning(stop, True, True)  # noqa: no-cover
