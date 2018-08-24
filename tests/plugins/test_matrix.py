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

from collections import OrderedDict

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import raises
from six import StringIO

from deployer import loader
from deployer.plugins import Matrix
from deployer.plugins import TopLevel


def test_plugin_matrix_invalid():
    assert_that(Matrix.valid({}), equal_to(False))
    assert_that(Matrix.valid(None), equal_to(False))
    assert_that(Matrix.valid(OrderedDict({'a': 'abc'})), equal_to(False))


def test_plugin_matrix_build():
    subject = Matrix.build({'matrix': {'tags': ['1'], 'tasks': {'echo': '12345'}}})
    assert_that(calling(next).with_args(subject), raises(StopIteration))


def test_plugin_matrix_fails_inner_task(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
        tasks:
          - fail: Exiting with style
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute()

    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, not contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('Exiting with style'))


def test_plugin_matrix_runs_with_two_elements(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
        tasks:
          - name: Testing task
            echo: Hello world.
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute()

    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('Hello world.'))
