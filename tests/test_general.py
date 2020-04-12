#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tests for tpDcc-tools-renamer
"""

import pytest

from tpDcc.tools.renamer import __version__


def test_version():
    assert __version__.get_version()
