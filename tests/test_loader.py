from hamcrest import assert_that
from hamcrest import instance_of
from six import StringIO

from deployer import loader


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
