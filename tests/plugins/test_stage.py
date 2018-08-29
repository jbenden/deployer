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
from hamcrest import instance_of
from six import StringIO

from deployer import loader
from deployer.cli import initialize
from deployer.context import Context
from deployer.plugins import Stage
from deployer.plugins import TopLevel


def test_plugin_stage_invalid():
    assert_that(Stage.valid({}), equal_to(False))
    assert_that(Stage.valid(None), equal_to(False))
    assert_that(Stage.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      stage:
        tags:
          - m1
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))

    stream = StringIO('''
    - name: test1
      stage:
        tasks:
          - name: test2
            matrix:
              tags:
                - m11
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_stage_build():
    subject = Stage.build({'stage': {'tasks': {'echo': '12345'}}})
    assert_that(next(subject), instance_of(Stage))


def test_plugin_stage_fails_inner_task(caplog):
    stream = StringIO('''
    - name: test1
      stage:
        tasks:
          - fail: Exiting with style
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        node.execute(None)

    assert_that(caplog.text, contains_string('Exiting with style'))


def test_plugin_stage_fails_inner_task_with_context(caplog):
    stream = StringIO('''
    - name: test1
      stage:
        tasks:
          - fail: Exiting with style
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('Exiting with style'))


def test_plugin_stage_does_not_create_scope(caplog):
    stream = StringIO('''
    - name: test1
      stage:
        scope: false
        tasks:
          - set:
              joe: benden

    - name: test2
      echo: "{{ joe }}"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| benden'))
