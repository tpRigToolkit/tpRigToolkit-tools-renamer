#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpDcc-tools-renamer client implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpDcc.core import client
from tpDcc.libs.python import python, path as path_utils
import tpDcc.libs.nameit


class RenamerClient(client.DccClient, object):

    PORT = 16231

    # =================================================================================================================
    # OVERRIDES
    # =================================================================================================================

    def _get_paths_to_update(self):
        paths_to_update = super(RenamerClient, self)._get_paths_to_update()

        paths_to_update['tpDcc.libs.nameit'] = path_utils.clean_path(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(tpDcc.libs.nameit.__file__)))))

        return paths_to_update

    # =================================================================================================================
    # BASE
    # =================================================================================================================

    def simple_rename(self, new_name, nodes=None, rename_shape=True):
        cmd = {
            'cmd': 'simple_rename',
            'new_name': new_name,
            'nodes': python.force_list(nodes),
            'rename_shape': rename_shape
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def add_prefix(self, prefix_text, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'add_prefix',
            'prefix_text': prefix_text,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_prefix(self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_prefix',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_first(self, count, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_first',
            'count': count,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_last(self, count, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_last',
            'count': count,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def add_suffix(self, suffix_text, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'add_suffix',
            'suffix_text': suffix_text,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_suffix(self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_suffix',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def replace_padding(self, pad, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'replace_padding',
            'pad': pad,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def append_padding(self, pad, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'append_padding',
            'pad': pad,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def change_padding(self, pad, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'change_padding',
            'pad': pad,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def add_side(self, side, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'add_side',
            'side': side,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def add_replace_namespace(
            self, namespace, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'add_replace_namespace',
            'namespace': namespace,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_namespace(
            self, namespace, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_namespace',
            'namespace': namespace,
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def search_and_replace(self, search_str, replace_str, nodes=None):
        cmd = {
            'cmd': 'search_and_replace',
            'search': search_str,
            'replace': replace_str,
            'nodes': python.force_list(nodes)
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def automatic_suffix(
            self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'automatic_suffix',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def make_unique_name(
            self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'make_unique_name',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_all_numbers(
            self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_all_numbers',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def remove_trail_numbers(
            self, rename_shape=True, hierarchy_check=False, only_selection=True, filter_type=None):
        cmd = {
            'cmd': 'remove_trail_numbers',
            'rename_shape': rename_shape,
            'hierarchy_check': hierarchy_check,
            'only_selection': only_selection,
            'filter_type': filter_type
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def clean_unused_namespaces(self):
        cmd = {
            'cmd': 'clean_unused_namespaces'
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def open_namespace_editor(self):
        cmd = {
            'cmd': 'open_namespace_editor'
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def open_reference_editor(self):
        cmd = {
            'cmd': 'open_reference_editor'
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']

    def rename(self):
        cmd = {
            'cmd': 'rename'
        }

        reply_dict = self.send(cmd)

        if not self.is_valid_reply(reply_dict):
            return False

        return reply_dict['success']
