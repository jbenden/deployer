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
from hamcrest import raises
from six import StringIO

from deployer import loader
from deployer.plugins import TopLevel


def test_plugin_top_level_invalid():
    assert_that(TopLevel.valid({}), equal_to(False))
    assert_that(TopLevel.valid(None), equal_to(False))
    stream = StringIO('''
    - name: test1
    ''')
    document = loader.ordered_load(stream)
    assert_that(TopLevel.valid(document), equal_to(False))


def test_plugin_top_level_valid_empty_list():
    assert_that(TopLevel.valid([]), equal_to(True))


def test_plugin_top_level_build_list_broken():
    subject = TopLevel.build([{}])

    from deployer.plugins.plugin import InvalidNode

    for node in subject:
        assert_that(calling(node.execute).with_args(None), raises(InvalidNode))


def test_plugin_top_level_build_ordereddict_list_broken():
    subject = TopLevel.build([OrderedDict({'name': 'Testing'})])

    from deployer.plugins.plugin import InvalidNode

    for node in subject:
        assert_that(calling(node.execute).with_args(None), raises(InvalidNode))


def test_plugin_top_level_build_errored_plugin():
    subject = TopLevel.build([OrderedDict({'name': 'Testing', 'env': {'a': 123}})])

    from deployer.plugins.plugin import FailedValidation

    for node in subject:
        assert_that(calling(node.execute).with_args(None), raises(FailedValidation))
