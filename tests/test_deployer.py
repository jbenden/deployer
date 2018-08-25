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

from deployer.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0


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


def test_exec_with_broken_file():
    runner = CliRunner()
    result = runner.invoke(main, ['exec', __file__])

    assert result.exit_code == 2
