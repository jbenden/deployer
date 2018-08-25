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

import sys

from hamcrest import assert_that
from hamcrest import calling
from hamcrest import equal_to
from hamcrest import raises
from jinja2.exceptions import TemplateSyntaxError
from jinja2.exceptions import UndefinedError

from deployer.context import Context
from deployer.rendering import BooleanExpression
from deployer.rendering import render


def test_rendering_invalid_template():
    fixture = """{{ a"""

    assert_that(calling(render).with_args(fixture), raises(TemplateSyntaxError))


def test_rendering_invalid_template_variable():
    fixture = """{{ nofunc(1) }}"""

    assert_that(calling(render).with_args(fixture), raises(UndefinedError))


def test_rendering_passthrough_string():
    fixture = """Testing string."""
    subject = render(fixture)

    assert_that(subject, equal_to(fixture))


def test_rendering_one_variable():
    fixture = """Hello {{ a }}."""
    subject = render(fixture, a="World")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_two_variables():
    fixture = """{{ b }} {{ a }}."""
    subject = render(fixture, a="World", b="Hello")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_one_indirection():
    fixture = """{{ a }}."""
    subject = render(fixture, a="{{ b }}", b="Hello World")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_two_indirections():
    fixture = """{{ a }}."""
    subject = render(fixture, a="{{ b }}", b="{{ c }}", c="Hello World")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_passthrough_raw_string():
    fixture = """{% raw %}Testing string.{% endraw %}"""
    subject = render(fixture)

    assert_that(subject, equal_to("Testing string."))


def test_rendering_passthrough_raw_string_and_variable():
    fixture = """{% raw %}Testing {% endraw %}{{ a }}"""
    subject = render(fixture, a='''{% raw %}{{ string }}.{% endraw %}''')

    assert_that(subject, equal_to("Testing {{ string }}."))


def test_rendering_raw_one_variable():
    fixture = """Hello {{ env.a }}."""
    subject = render(fixture, env={'a': '''{% raw %}World{% endraw %}'''})

    assert_that(subject, equal_to("Hello World."))


def test_rendering_raw_two_variables():
    fixture = """{{ b }} {{ a }}."""
    subject = render(fixture, a="{% raw %}Worl{% endraw %}d", b="He{% raw %}llo{% endraw %}")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_raw_one_indirection():
    fixture = """{{ a }}."""
    subject = render(fixture, a="{{ b }}", b="{% raw %}Hello World{% endraw %}")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_raw_two_indirections():
    fixture = """{{ a }}."""
    subject = render(fixture, a="{{ b }}", b="{{ c }}", c="{% raw %}Hello World{% endraw %}")

    assert_that(subject, equal_to("Hello World."))


def test_rendering_simple_context():
    context = Context()
    fixture = """{{ platform }}"""
    subject = render(fixture, **context.variables.last())

    assert_that(subject, equal_to(sys.platform.lower()))


def test_rendering_simple_boolean_true():
    context = Context()
    fixture = BooleanExpression("""True""")
    subject = fixture.evaluate(context)

    assert_that(subject, equal_to(True))


def test_rendering_simple_boolean_false():
    context = Context()
    fixture = BooleanExpression("""False""")
    subject = fixture.evaluate(context)

    assert_that(subject, equal_to(False))


def test_rendering_invalid_expression_raises():
    context = Context()
    fixture = BooleanExpression("""{{ False }}""")

    assert_that(calling(fixture.evaluate).with_args(context), raises(RuntimeError))
