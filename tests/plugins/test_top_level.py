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
from hamcrest import equal_to
from hamcrest import instance_of
from hamcrest import raises
from hamcrest import starts_with
from six import StringIO

from deployer import loader
from deployer.cli import initialize
from deployer.plugins import TopLevel
from deployer.plugins.echo import Echo


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


def test_plugin_top_level_invalid():
    assert_that(TopLevel.valid({}), equal_to(False))
    assert_that(TopLevel.valid(None), equal_to(False))


def test_plugin_top_level_valid_empty_list():
    assert_that(TopLevel.valid([]), equal_to(True))


def test_plugin_top_level_build_empty_list():
    subject = TopLevel.build([])
    assert_that(calling(next).with_args(subject), raises(StopIteration))


def test_plugin_top_level_build_list_broken():
    subject = TopLevel.build([{}])
    assert_that(calling(next).with_args(subject), raises(RuntimeError))


def test_plugin_top_level_build_ordereddict_list_broken():
    subject = TopLevel.build([OrderedDict({'name': 'Testing'})])
    assert_that(calling(next).with_args(subject), raises(RuntimeError))
