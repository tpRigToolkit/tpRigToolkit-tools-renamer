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

    def simple_rename(self, data, reply):
        new_name = data.get('new_name', '')
        if not new_name:
            reply['msg'] = 'Please type a new name and try the operation again!'
            reply['success'] = False
            return

        nodes = data.get('nodes', list())
        if not nodes:
            nodes = dcc.selected_nodes()
        for node in nodes:
            dcc.rename_node(node, new_name)

        reply['success'] = True

    def add_prefix(self, data, reply):

        prefix_text = data.get('prefix_text', '')
        if not prefix_text:
            reply['success'] = False
            reply['msg'] = 'No prefix to add defined.'
            return

        selection_only = data.get('only_selection', True)

        dcc.add_name_prefix(prefix=prefix_text, selection_only=selection_only)
