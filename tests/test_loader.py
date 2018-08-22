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

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import instance_of
from six import StringIO

from deployer import loader
from deployer.plugins import TopLevel


def test_top_level_is_a_list():
    stream = StringIO('''
- name: test1
- name: test2
- name: test3
    ''')
    document = loader.ordered_load(stream)
    assert_that(document, instance_of(list))


def test_top_level_is_a_list_with_dict():
    stream = StringIO('''
- name: test1
- name: test2
- name: test3
    ''')
    document = loader.ordered_load(stream)
    assert_that(document, instance_of(list))
    assert_that(document[0], instance_of(dict))


def test_top_level_is_an_ordered_list_of_dict():
    stream = StringIO('''
- name: test1
- name: test2
- name: test3
    ''')
    document = loader.ordered_load(stream)
    assert_that(document, instance_of(list))
    assert_that(document[0], instance_of(dict))
    assert_that(document[0]['name'], equal_to('test1'))
    assert_that(document[1], instance_of(dict))
    assert_that(document[1]['name'], equal_to('test2'))
    assert_that(document[2], instance_of(dict))
    assert_that(document[2]['name'], equal_to('test3'))


def test_top_level_is_created():
    stream = StringIO('''
    - name: test1
    - name: test2
    - name: test3
        ''')
    document = loader.ordered_load(stream)
    root = TopLevel(document)
    assert_that(root.validate(), equal_to(True))
