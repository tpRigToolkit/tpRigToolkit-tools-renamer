#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpDcc-tools-renamer server implementation for 3ds Max
"""

from __future__ import print_function, division, absolute_import

from tpDcc import dcc
from tpDcc.core import server


class RenamerServer(server.DccServer, object):
    PORT = 16231
