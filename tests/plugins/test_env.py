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

import os
from collections import OrderedDict

import pytest
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import instance_of
from six import StringIO

from deployer import loader
from deployer.plugins import Env
from deployer.plugins import TopLevel


@pytest.fixture
def capenv(request):
    # copy the current environment
    prev_env = os.environ.copy()

    # perform the test we have
    yield

    # restore environment
    for key, value in os.environ.copy().items():
        try:
            os.unsetenv(key)
        except AttributeError:                                           # noqa: no-cover
            pass                                                         # noqa: no-cover
        del os.environ[key]
    for key, value in prev_env.items():
        os.putenv(key, value)
        os.environ[key] = value


def test_plugin_env_invalid():
    assert_that(Env.valid({}), equal_to(False))
    assert_that(Env.valid(None), equal_to(False))
    assert_that(Env.valid(OrderedDict({'a': 'abc'})), equal_to(False))


def test_plugin_env_build():
    subject = Env.build({'env': {'set': {'a': '12345'}}})
    assert_that(next(subject), instance_of(Env))


def test_plugin_env_unset_all_and_adds_one_via_list(capenv):
    stream = StringIO('''
    - name: test1
      env:
        set:
            "Joe": "Benden"
        unset:
            - '*'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute()

    assert_that('Joe' in os.environ, equal_to(True))
    assert_that(len(os.environ), equal_to(1))


def test_plugin_env_unset_all_and_adds_one_via_str(capenv):
    stream = StringIO('''
    - name: test1
      env:
        set:
            "Joe": "Benden"
        unset: '*'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute()

    assert_that('Joe' in os.environ, equal_to(True))
    assert_that(len(os.environ), equal_to(1))


def test_plugin_env_set_one(capenv):
    stream = StringIO('''
    - name: test1
      env:
        set:
            "Joe": "Blarg"
    - name: test2
      echo: hi2
    - name: test3
      echo: hi3
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute()

    assert_that('Joe' in os.environ, equal_to(True))


def test_plugin_env_unset_filter(capenv):
    stream = StringIO('''
    - name: test1
      env:
        unset: 'J*'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    os.environ['Joe'] = '123'
    os.putenv('Joe', '123')

    for node in nodes:
        node.execute()

    assert_that(os.getenv('Joe', None), equal_to(None))
