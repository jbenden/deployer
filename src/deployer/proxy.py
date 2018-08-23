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
Proxy pattern wrapper module.

.. moduleauthor:: Joseph Benden <joe@benden.us>

:copyright: (c) Copyright 2018 by Joseph Benden.
:license: Apache License 2.0, see LICENSE.txt for full details.
"""


class Proxy(object):
    """Wrapper class to create Proxy objects."""

    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        """Init method."""
        object.__setattr__(self, "_obj", obj)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        """Get attribute."""
        if not name.startswith("_") and hasattr(type(self), name):
            return object.__getattribute__(self, name)                   # noqa: no-cover
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        """Delete attribute."""
        delattr(object.__getattribute__(self, "_obj"), name)             # noqa: no-cover

    def __setattr__(self, name, value):
        """Set an attribute."""
        setattr(object.__getattribute__(self, "_obj"), name, value)      # noqa: no-cover

    def __nonzero__(self):
        """Is non-zero."""
        return bool(object.__getattribute__(self, "_obj"))               # noqa: no-cover

    def __str__(self):
        """Get the string value of object."""
        return str(object.__getattribute__(self, "_obj"))                # noqa: no-cover

    def __repr__(self):
        """Get the string representation of the object."""
        return repr(object.__getattribute__(self, "_obj"))               # noqa: no-cover

    def __hash__(self):
        """Hash value of the object."""
        return hash(object.__getattribute__(self, "_obj"))               # noqa: no-cover

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):                              # noqa: no-cover
        """Create a proxy for the given class."""
        def make_method(name):                                           # noqa: no-cover
            def method(self, *args, **kw):                               # noqa: no-cover
                return getattr(object.__getattribute__(self, "_obj"),    # noqa: no-cover
                               name)(*args, **kw)                        # noqa: no-cover

            return method                                                # noqa: no-cover

        namespace = {}                                                   # noqa: no-cover
        for name in cls._special_names:                                  # noqa: no-cover
            if hasattr(theclass, name):  # and not hasattr(cls, name):   # noqa: no-cover
                namespace[name] = make_method(name)                      # noqa: no-cover
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        Create a proxy instance referencing `obj`.

        The parameters (obj, *args, **kwargs) are all passed to this class' `__init__`,
        so deriving classes can define an `__init__` method of their own.

        .. note::

        `_class_proxy_cache` is unique per deriving class (each deriving class must
        hold its own cache).
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        # theclass.__init__(ins, obj, *args, **kwargs)
        return ins
