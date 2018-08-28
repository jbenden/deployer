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
from deployer.plugins import Shell
from deployer.plugins import TopLevel
from deployer.util import stop_reactor

IS_WINDOWS = sys.platform.lower().startswith('win')


@pytest.fixture(scope="session")
def reactor(request):
    initialize()
    yield
    stop_reactor(None)


def test_plugin_shell_invalid():
    assert_that(Shell.valid({}), equal_to(False))
    assert_that(Shell.valid(None), equal_to(False))
    assert_that(Shell.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      shell: False
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_shell_build():
    subject = Shell.build({'shell': {'script': 'echo'}})
    assert_that(next(subject), instance_of(Shell))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_shell_silent_on_unix(caplog, reactor):
    stream = StringIO('''
    - name: test1
      shell:
        script: echo Hello
        executable: bash
        silent: true
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, not contains_string('| Hello'))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_shell_on_unix(caplog, reactor):
    stream = StringIO('''
    - name: test1
      shell:
        script: echo Hello
        executable: bash
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| Hello'))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_shell_on_unix_with_exact_shell(caplog, reactor):
    stream = StringIO('''
    - name: test1
      shell:
        script: echo Hello
        executable: /bin/sh
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| Hello'))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_shell_on_unix_nonzero_return(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      shell:
        script: "false"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_plugin_shell_on_unix_bad(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      shell:
        script: /nonexistent
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on non-Windows')
def test_plugin_shell_on_win(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      shell:
        script: \'echo Hello world\'
        executable: cmd
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| Hello world'))


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on non-Windows')
def test_plugin_shell_on_win_bad(caplog, reactor):  # noqa: no-cover
    stream = StringIO('''
    - name: test1
      shell:
        script: sdfsdfdsf329909092
        executable: cmd
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string("'failure'"))
