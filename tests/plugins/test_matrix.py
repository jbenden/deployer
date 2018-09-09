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
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import has_entry
from hamcrest import instance_of
from hamcrest import is_not
from six import StringIO

from deployer import loader
from deployer.cli import initialize
from deployer.context import Context
from deployer.plugins import Matrix
from deployer.plugins import TopLevel


def test_plugin_matrix_invalid():
    assert_that(Matrix.valid({}), equal_to(False))
    assert_that(Matrix.valid(None), equal_to(False))
    assert_that(Matrix.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))

    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
        tasks:
          - name: test2
            matrix:
              tags:
                - m11
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_matrix_build():
    subject = Matrix.build({'matrix': {'tags': ['1'], 'tasks': {'echo': '12345'}}})
    assert_that(next(subject), instance_of(Matrix))


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
        node.execute(None)

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

    assert_that(TopLevel.valid(document), equal_to(True))

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute(None)

    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('Hello world.'))


def test_plugin_matrix_runs_with_two_elements_and_contains_tags(caplog):
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

    assert_that(TopLevel.valid(document), equal_to(True))

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

        assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
        assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))

    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('Hello world.'))

    assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
    assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))


def test_plugin_matrix_runs_with_two_elements_and_contains_dict_tags(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          m1:
            Joe: m1
          m2:
            Joe: m2
        tasks:
          - name: Testing task
            echo: Hello world.
    ''')
    document = loader.ordered_load(stream)

    assert_that(TopLevel.valid(document), equal_to(True))

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

        assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
        assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))

    assert_that(caplog.text, contains_string('Joe'))
    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('Hello world.'))

    assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
    assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))


def test_plugin_matrix_runs_with_two_matrices_and_contains_tags(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
        tasks:
          - name: test2
            matrix:
              tags:
                - m3
              tasks:
                - name: Testing task
                  echo: "Hello world. {{ matrix_tag }}"
    ''')
    document = loader.ordered_load(stream)

    assert_that(TopLevel.valid(document), equal_to(True))

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

        assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
        assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))

    assert_that(caplog.text, contains_string('entry: m1'))
    assert_that(caplog.text, contains_string('entry: m2'))
    assert_that(caplog.text, contains_string('entry: m3'))
    assert_that(caplog.text, contains_string('Hello world. m3'))

    assert_that(context.variables.last(), not has_entry('matrix_tag', 'm2'))
    assert_that(context.variables.last(), not has_entry('matrix_list', ['m2']))


def test_plugin_matrix_runs_with_two_matrices_with_multiple_attempts(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
        tasks:
          - name: test2
            matrix:
              tags:
                - m3
              tasks:
                - name: Testing task
                  echo: Hello world.
                  attempts: 3
    ''')
    document = loader.ordered_load(stream)

    assert_that(TopLevel.valid(document), equal_to(True))

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('Hello world.'))
    assert_that(caplog.text, is_not(contains_string('failure')))
