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

import os

from click.testing import CliRunner
from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import is_not

from deployer.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0


def test_main_shows_debugging_messages():
    runner = CliRunner()
    result = runner.invoke(main, ['--debug'])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('DEBUG'))


def test_main_shows_no_messages():
    runner = CliRunner()
    result = runner.invoke(main, ['--silent'])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, equal_to(''))


def test_validate_with_simple_example():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['validate', example])

    assert result.exit_code == 0


def test_validate_with_broken_yaml():
    runner = CliRunner()
    result = runner.invoke(main, ['validate', __file__])

    assert result.exit_code == 1


def test_exec_with_simple_example():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', example])

    assert result.exit_code == 0


def test_exec_with_simple_failure_example():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-failure.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', example])

    assert result.exit_code == 1


def test_exec_with_broken_file():
    runner = CliRunner()
    result = runner.invoke(main, ['exec', __file__])

    assert result.exit_code == 2


def test_exec_with_simple_tagging_example_selected_simple_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', '--tag=simple', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, not contains_string('Hello Earth.'))


def test_exec_with_simple_tagging_example_selected_earth_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', '--tag=earth', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, not contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_tagging_example_selected_both_tags():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', '--tag=earth', '--tag=simple', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_selected_simple_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', '--tag=simple', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, not contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_selected_earth_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['exec', '--tag=earth', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, not contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_selected_both_tags():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--tag=earth', '--tag=simple', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_selected_matrix_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--matrix-tags=m*', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_multi_selected_matrix_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--matrix-tags=m*,*', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_multi_non_selected_matrix_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--matrix-tags=a,*,*', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, is_not(contains_string('Hello World.')))
    assert_that(result.output, contains_string('Hello Earth.'))
    assert_that(result.output,
                contains_string('Skipping because this matrix item does not have a user-selected matrix tag'))


def test_exec_with_simple_matrix_tagging_example_not_selected_matrix_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--matrix-tags=simple', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, not contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))


def test_exec_with_simple_matrix_tagging_example_not_selected_empty_matrix_tag():
    __path__ = os.path.dirname(__file__)
    example = os.path.join(__path__, '..', 'examples', 'simple-matrix-tagging.yaml')

    runner = CliRunner()
    result = runner.invoke(main, ['--debug', 'exec', '--matrix-tags=', example])

    assert_that(result.exit_code, equal_to(0))
    assert_that(result.output, not contains_string('Hello World.'))
    assert_that(result.output, contains_string('Hello Earth.'))
