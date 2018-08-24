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

import logging
import re

from jinja2 import Environment
from jinja2.exceptions import TemplateSyntaxError
from jinja2.exceptions import UndefinedError
from six import string_types

LOGGER = logging.getLogger(__name__)


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
        if isinstance(value, string_types) and '{' in value:
            if raw_sentinal in value:
                value = value.replace(raw_sentinal, '')
                value = raw_regexp.sub(('{%% raw %%}%s' % raw_sentinal), value)
                return value

            value = raw_regexp.sub(('{%% raw %%}%s' % raw_sentinal), value)
            value = environment.from_string(value).render(kwargs)
        return value

    try:
        environment = Environment(autoescape=False, finalize=finalize)  # nosec
        environment.filters['render'] = render

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
