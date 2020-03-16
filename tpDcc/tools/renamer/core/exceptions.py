#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains exceptions used by tpRenamer
"""

from __future__ import print_function, division, absolute_import

import tpDcc as tp


class RenameException(Exception):
    """
    Custom exception class that will handle errors when renaming elements using tpRenamer tool
    """

    def __init__(self, nodes):

        error_text = '======= Renamer: Failed to rename one or more nodes ======='
        if not hasattr(nodes, '__iter__'):
            nodes = [nodes]
        for node in nodes:
            if not tp.Dcc.object_exists(node):
                error_text += "\t'%s' no longer exists.\n" % node
            elif tp.Dcc.node_is_locked(node):
                error_text += "\t'%s' is locked.\n" % node
            else:
                error_text += "\t'%s' failure unknows.\n" % node

        Exception.__init__(self, error_text)
