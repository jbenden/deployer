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

"""
A recursive Jinja2 rendering engine.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""

import ast
import collections
import logging
import os
import re
import sys

from jinja2 import Environment
from jinja2.exceptions import TemplateSyntaxError
from jinja2.exceptions import UndefinedError
from jinja2.runtime import StrictUndefined
from six import string_types

LOGGER = logging.getLogger(__name__)

# Based on: Using ast and whitelists to make python's eval() safe?
# https://stackoverflow.com/questions/12523516/using-ast-and-whitelists-to-make-pythons-eval-safe

SAFE_FX = {
    'OrderedDict': collections.OrderedDict,
}

SAFE_NODES = set(
    (
        ast.Add,
        ast.BinOp,
        # ast.Call,
        ast.Compare,
        ast.Dict,
        ast.Div,
        ast.Expression,
        ast.List,
        ast.Load,
        ast.Mult,
        ast.Num,
        ast.Name,
        ast.Str,
        ast.Sub,
        ast.USub,
        ast.Tuple,
        ast.UnaryOp,
    )
)

# AST node types were expanded after 2.6
if sys.version_info[:2] >= (2, 7):  # noqa: no-cover
    SAFE_NODES.update(
        set(
            (ast.Set,)
        )
    )

# And in Python 3.4 too
if sys.version_info[:2] >= (3, 4):  # noqa: no-cover
    SAFE_NODES.update(
        set(
            (ast.NameConstant,)
        )
    )


class CleansingNodeVisitor(ast.NodeVisitor):  # noqa: no-cover
    """Cleaning AST node visitor."""

    def generic_visit(self, node):
        """All nodes, not matching another visitor."""
        if type(node) not in SAFE_NODES:
            raise Exception("%s not in SAFE_NODES" % type(node))
        super(CleansingNodeVisitor, self).generic_visit(node)

    def visit_Call(self, call):
        """Call AST Node visitor."""
        if call.func.id not in SAFE_FX:
            raise Exception("Unknown function: %s" % call.func.id)


def my_safe_eval(s):
    """Safely evaluate a Pythonic expression string."""
    tree = ast.parse(s, mode='eval')
    cnv = CleansingNodeVisitor()
    cnv.visit(tree)
    compiled = compile(tree, s, "eval")
    return(eval(compiled, SAFE_FX, dict({})))  # nosec


class BooleanExpression:
    """Simplistic boolean conditional evaluation through the Jinja2 templating engine."""

    INVALID_SEQUENCES = ['{{', '}}', '{%', '%}']

    def __init__(self, expression):
        """Ctor."""
        self._expression = expression

    def evaluate(self, context):
        """Evaluate the boolean expression through the templating system, returning the result."""
        if isinstance(self._expression, bool):
            return self._expression

        for invalid in self.INVALID_SEQUENCES:
            if invalid in self._expression:
                raise RuntimeError("Expression must not contain Jinja2 templating characters:\n%s" % self._expression)

        template = "{%%- if %s %%}True{%% else %%}False{%% endif -%%}" % self._expression
        result = render(template, **context.variables.last().copy())

        if result == 'True':
            return True
        elif result == 'False':
            return False

        raise RuntimeError("Jinja2 returned an invalid result for expression:\n%s" % self._expression)  # noqa: no-coverage


def render(value, **kwargs):
    """Use Jinja2 for recursive, template-based rendering.

    Args:
        value (str): the template to be rendered.
        kwargs (dict): named parameters representing available variables
                       inside the template.

    .. note::

    The pipeline process is all about shell code and therefore auto-escaping
    wouldn't help. Usually a pipeline runs in a isolated environment
    and there should not be any injection from outside; that's why: nosec.
    """
    raw_sentinal = 'Z6db7f9f90d8c7519dcbb6ac0dd828a0f2a8ab18a34ab8b0cae0fb6c0469a1e19Z'
    raw_regexp = re.compile(r"\{%\s*raw\s*%\}")
    environment = None

    def finalize(value):
        """Our internal Jinja2 finalizer; which recursively renders."""
        if isinstance(value, string_types) and any(x in value for x in ['{{', '}}', '{%', '%}']):
            if raw_sentinal in value:
                value = value.replace(raw_sentinal, '')
                value = raw_regexp.sub(('{%% raw %%}%s' % raw_sentinal), value)
                return value

            value = raw_regexp.sub(('{%% raw %%}%s' % raw_sentinal), value)
            value = environment.from_string(value).render(kwargs)
        return value

    try:
        environment = Environment(autoescape=False, undefined=StrictUndefined, finalize=finalize)  # nosec
        environment.filters['render'] = render

        kwargs['env'] = os.environ

        if isinstance(value, string_types) and 'raw' in value:
            value = raw_regexp.sub(('{%% raw %%}%s' % raw_sentinal), value)

        rendered_value = environment.from_string(value).render(kwargs)
        if raw_sentinal in rendered_value:
            rendered_value = rendered_value.replace(raw_sentinal, '')

        return rendered_value
    except UndefinedError as exception:
        LOGGER.error("render(undefined): %s", exception)
        raise
    except TemplateSyntaxError as exception:
        LOGGER.error("render(syntax error): %s", exception)
        raise
