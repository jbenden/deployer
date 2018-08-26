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

import pytest
from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import raises
from twisted.internet.error import ProcessTerminated

from deployer.util import start_reactor
from deployer.util import stop_reactor
from deployer.util import sync_check_output

IS_WINDOWS = sys.platform.lower().startswith('win')


@pytest.fixture(scope="module")
def reactor(request):
    r = start_reactor()
    yield
    stop_reactor(r)


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_util_unix_echo_works(reactor):
    subject = sync_check_output(['/bin/echo', 'hello world'])  # noqa: no-cover
    assert_that(subject, equal_to("hello world"))  # noqa: no-cover


@pytest.mark.skipif(IS_WINDOWS, reason='Irrelevant on non-unix')
def test_util_unix_nonexisting_fails(reactor):
    assert_that(calling(sync_check_output).with_args(['/nonexistent', 'hello world']), raises(ProcessTerminated))  # noqa: no-cover


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on unix')
def test_util_win_echo_works(reactor):
    assert_that(sync_check_output(["\\Windows\\System32\\cmd.exe", "/c", "echo", "hello", "world"]), equal_to("hello world"))  # noqa: no-cover


@pytest.mark.skipif(not IS_WINDOWS, reason='Irrelevant on unix')
def test_util_win_nonexisting_fails(reactor):
    assert_that(calling(sync_check_output).with_args(["sdfsdfdsf329909092"]), raises(ProcessTerminated))  # noqa: no-cover
