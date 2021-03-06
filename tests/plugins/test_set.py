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
from deployer.plugins import Set
from deployer.plugins import TopLevel


def test_plugin_set_invalid():
    assert_that(Set.valid({}), equal_to(False))
    assert_that(Set.valid(None), equal_to(False))
    assert_that(Set.valid(OrderedDict({'a': 'abc'})), equal_to(False))

    initialize()

    stream = StringIO('''
    - name: test1
      set:
        - i1
        - i2
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_set_build():
    subject = Set.build({'set': {'a': 'b'}})
    assert_that(next(subject), instance_of(Set))


def test_plugin_set_works(caplog):
    stream = StringIO('''
    - name: test1
      set:
        joe: benden

    - name: test2
      echo: '{{ joe }}'
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| benden'))


def test_plugin_set_list_with_items(caplog):
    stream = StringIO('''
    - name: test1
      set:
        bits:
          - 1
          - 2
          - 3

    - name: test2
      echo: '--{{ item }}--'
      with_items: "{{ bits }}"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for node in nodes:
        node.execute(context)

    assert_that(caplog.text, contains_string('| --1--'))
    assert_that(caplog.text, contains_string('| --2--'))
    assert_that(caplog.text, contains_string('| --3--'))
