"""
Common complex types

"""

import typing

StrDict = typing.Dict[str, str]

# This is a work in progress
# If anything has a very specific type, build it here.
# It can help us later on with CI linting and strict runtime checking
# Refer to https://docs.python.org/3/library/typing.html for help

# Use for any parsed JSON, or nested dict structure,
# until the true structure is known
ComplexDict = typing.Dict[str, typing.Any]
