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
from deployer.plugins import Continue
from deployer.plugins import TopLevel


def test_plugin_continue_invalid():
    assert_that(Continue.valid({}), equal_to(False))
    assert_that(Continue.valid(None), equal_to(False))
    assert_that(Continue.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      continue:
        - i1
        - i2
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_continue_build():
    subject = Continue.build({'continue': {'when': ['False']}})
    assert_that(next(subject), instance_of(Continue))


def test_plugin_continue_with_matrix_works(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
          - m3
        tasks:
          - name: test1
            continue:
              when:
                - 'False'
                - '1 == 1'

          - echo: "---{{ matrix_tag }}---"

    - echo: '---WORKS---'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, not contains_string('---m1---'))
    assert_that(caplog.text, not contains_string('---m2---'))
    assert_that(caplog.text, not contains_string('---m3---'))
    assert_that(caplog.text, contains_string('---WORKS---'))


def test_plugin_continue_will_continue(caplog):
    stream = StringIO('''
    - name: test1
      matrix:
        tags:
          - m1
          - m2
          - m3
        tasks:
          - name: test1
            continue:
              when:
                - 'False'

          - echo: "---{{ matrix_tag }}---"

    - echo: '---WORKS---'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('---m1---'))
    assert_that(caplog.text, contains_string('---m2---'))
    assert_that(caplog.text, contains_string('---m3---'))
    assert_that(caplog.text, contains_string('---WORKS---'))


def test_plugin_continue_with_stage_works(caplog):
    stream = StringIO('''
    - name: test1
      stage:
        tasks:
          - name: test1
            continue:
              when:
                - '1 == 1'

          - echo: "---FAILED---"

    - echo: '---WORKS---'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, not contains_string('---FAILED---'))
    assert_that(caplog.text, contains_string('---WORKS---'))
