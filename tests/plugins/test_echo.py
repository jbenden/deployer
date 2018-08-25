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

import platform
from collections import OrderedDict

from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import instance_of
from hamcrest import starts_with
from six import StringIO

from deployer import loader
from deployer.cli import initialize
from deployer.context import Context
from deployer.plugins import Fail
from deployer.plugins import TopLevel
from deployer.plugins.echo import Echo
from deployer.plugins.matrix import Matrix


def test_plugin_fail_invalid():
    assert_that(Fail.valid({}), equal_to(False))
    assert_that(Fail.valid(None), equal_to(False))
    assert_that(Fail.valid(OrderedDict({'a': 'abc'})), equal_to(False))


def test_plugin_top_level_is_created():
    initialize()
    stream = StringIO('''
    - name: test1
      echo: hi1
    - name: test2
      echo: hi2
    - name: test3
      echo: hi3
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for node in nodes:
        assert_that(node, instance_of(Echo))
        assert_that(node.msg, starts_with("hi"))


def test_plugin_echo_invalid():
    assert_that(Echo.valid({}), equal_to(False))
    assert_that(Echo.valid(None), equal_to(False))
    assert_that(Echo.valid(OrderedDict({'a': 'abc'})), equal_to(False))


def test_plugin_echo_valid():
    assert_that(Echo.valid(OrderedDict({'echo': 'Testing'})), equal_to(True))


def test_plugin_echo_build():
    subject = Echo.build({'echo': 'Testing'})
    assert_that(next(subject), instance_of(Echo))


def test_plugin_echo_works(caplog):
    # NOTE: because no toplevel is called, we do NOT proxy!
    subject = next(Echo.build(OrderedDict({'echo': 'Testing'})))
    subject.execute(None)
    assert_that(len(caplog.records), equal_to(1))
    assert_that(caplog.records[0].message, equal_to("| Testing"))


def test_plugin_top_level_produces_logging(caplog):
    stream = StringIO('''
    - name: test0
      echo: hi1
    - name: test1
      echo: hi2
    - name: test2
      echo: hi3
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(None)

        assert_that(len(caplog.records), equal_to(3))
        assert_that(caplog.records[0].message, starts_with("test%d is starting" % index))
        assert_that(caplog.records[2].message, starts_with("test%d has finished" % index))

        caplog.clear()


def test_plugin_echo_renders_node(caplog):
    stream = StringIO('''
    - name: test0
      echo: "{{ node }}"
    - name: test1
      echo: "{{ node }}"
    - name: test2
      echo: "{{ node }}"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(context)

        assert_that(len(caplog.records), equal_to(3))
        assert_that(caplog.records[0].message, starts_with("test%d is starting" % index))
        assert_that(caplog.records[1].message, starts_with("| %s" % platform.node()))
        assert_that(caplog.records[2].message, starts_with("test%d has finished" % index))

        caplog.clear()


def test_plugin_matrix_renders_node(caplog):
    stream = StringIO('''
    - name: A simple test
      matrix:
        tags:
          - m1
        tasks:
          - name: test0
            echo: "{{ node }}"
          - name: test1
            echo: "{{ node }}"
          - name: test2
            echo: "{{ node }}"
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    m1 = next(nodes)
    assert_that(m1, instance_of(Matrix))
    m1.execute(context)

    assert_that(caplog.text, contains_string("| %s" % platform.node()))


def test_plugin_echo_with_false_when(caplog):
    stream = StringIO('''
    - name: test0
      echo: "{{ node }}"
      when: False
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(context)

        assert_that(len(caplog.records), equal_to(0))


def test_plugin_echo_with_true_when(caplog):
    stream = StringIO('''
    - name: test0
      echo: "{{ node }}"
      when: True
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(context)

        assert_that(len(caplog.records), equal_to(3))


def test_plugin_echo_with_simple_when(caplog):
    stream = StringIO('''
    - name: test0
      echo: "{{ node }}"
      when: nbcpus == 0
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(context)

        assert_that(len(caplog.records), equal_to(0))


def test_plugin_echo_renders_multiple_items(caplog):
    stream = StringIO('''
    - name: test0
      echo: "{{ item }}"
      with_items:
        - a-0
        - b-0
        - c-0
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        assert_that(node, instance_of(Echo))
        node.execute(context)

    assert_that(len(caplog.records), equal_to(9))
    assert_that(caplog.text, contains_string("| a-0"))
    assert_that(caplog.text, contains_string("| b-0"))
    assert_that(caplog.text, contains_string("| c-0"))


def test_plugin_fail_renders_multiple_items(caplog):
    stream = StringIO('''
    - name: test0
      fail: "{{ item }}"
      with_items:
        - a-0
        - b-0
        - c-0
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    context = Context()

    for index, node in enumerate(nodes):
        node.execute(context)

    assert_that(len(caplog.records), equal_to(3))
    assert_that(caplog.text, contains_string("| a-0"))
    assert_that(caplog.text, not contains_string("| b-0"))
    assert_that(caplog.text, not contains_string("| c-0"))


def test_plugin_fail_fails_rendering_multiple_items_without_a_context(caplog):
    stream = StringIO('''
    - name: test0
      fail: "{{ item }}"
      with_items:
        - a-0
        - b-0
        - c-0
    ''')
    document = loader.ordered_load(stream)

    nodes = TopLevel.build(document)

    for index, node in enumerate(nodes):
        node.execute(None)

    assert_that(len(caplog.records), equal_to(3))
    assert_that(caplog.text, contains_string("{{ item }}"))
