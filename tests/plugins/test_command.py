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

import sys
from collections import OrderedDict

import pytest
from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import instance_of
from six import StringIO

from deployer import loader
from deployer.cli import initialize
from deployer.context import Context
from deployer.plugins import Command
from deployer.plugins import TopLevel
from deployer.util import stop_reactor

IS_WINDOWS = sys.platform.lower().startswith('win')


@pytest.fixture(scope="session")
def reactor(request):
    initialize()
    yield
    stop_reactor(None)


def test_plugin_command_invalid():
    assert_that(Command.valid({}), equal_to(False))
    assert_that(Command.valid(None), equal_to(False))
    assert_that(Command.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      command: False
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_command_build():
    subject = Command.build({'command': {'true'}})
    assert_that(next(subject), instance_of(Command))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_command_on_unix(caplog, reactor):
    stream = StringIO('''
    - name: test1
      command: echo Hello
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| Hello'))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_command_on_unix_nonzero_return(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      command: "false"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_command_on_unix_bad(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      command: /nonexistent
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on non-Windows')
def test_plugin_command_on_win(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      command: "\Windows\System32\cmd.exe /c echo Hello world"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| Hello world'))


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on non-Windows')
def test_plugin_command_on_win_bad(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      command: sdfsdfdsf329909092
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))
