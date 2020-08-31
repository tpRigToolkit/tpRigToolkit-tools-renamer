#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpDcc-tools-renamer server implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import tpDcc as tp
from tpDcc.core import server

from tpDcc.dccs.maya.core import namespace, gui

LOGGER = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


class RenamerServer(server.DccServer, object):
    PORT = 16231

    def _process_command(self, command_name, data_dict, reply_dict):
        if command_name == 'simple_rename':
            self.simple_rename(data_dict, reply_dict)
        elif command_name == 'add_prefix':
            self.add_prefix(data_dict, reply_dict)
        elif command_name == 'remove_prefix':
            self.remove_prefix(data_dict, reply_dict)
        elif command_name == 'remove_first':
            self.remove_first(data_dict, reply_dict)
        elif command_name == 'add_suffix':
            self.add_suffix(data_dict, reply_dict)
        elif command_name == 'remove_suffix':
            self.remove_suffix(data_dict, reply_dict)
        elif command_name == 'remove_last':
            self.remove_last(data_dict, reply_dict)
        elif command_name == 'replace_padding':
            self.replace_padding(data_dict, reply_dict)
        elif command_name == 'append_padding':
            self.append_padding(data_dict, reply_dict)
        elif command_name == 'change_padding':
            self.change_padding(data_dict, reply_dict)
        elif command_name == 'add_side':
            self.add_side(data_dict, reply_dict)
        elif command_name == 'add_replace_namespace':
            self.add_replace_namespace(data_dict, reply_dict)
        elif command_name == 'remove_namespace':
            self.remove_namespace(data_dict, reply_dict)
        elif command_name == 'search_and_replace':
            self.search_and_replace(data_dict, reply_dict)
        elif command_name == 'automatic_suffix':
            self.automatic_suffix(data_dict, reply_dict)
        elif command_name == 'make_unique_name':
            self.make_unique_name(data_dict, reply_dict)
        elif command_name == 'remove_all_numbers':
            self.remove_all_numbers(data_dict, reply_dict)
        elif command_name == 'remove_trail_numbers':
            self.remove_trail_numbers(data_dict, reply_dict)
        elif command_name == 'clean_unused_namespaces':
            self.clean_unused_namespaces(data_dict, reply_dict)
        elif command_name == 'open_namespace_editor':
            self.open_namespace_editor(data_dict, reply_dict)
        elif command_name == 'open_reference_editor':
            self.open_reference_editor(data_dict, reply_dict)
        else:
            super(RenamerServer, self)._process_command(command_name, data_dict, reply_dict)

    def simple_rename(self, data, reply):

        new_name = data.get('new_name', '')
        if not new_name:
            reply['msg'] = 'Please type a new name and try the operation again!'
            reply['success'] = False
            return

        rename_shape = data.get('rename_shape', True)
        nodes = data.get('nodes', list())
        if not nodes:
            nodes = tp.Dcc.selected_nodes()
        for node in nodes:
            tp.Dcc.rename_node(node, new_name, rename_shape=rename_shape)

        reply['success'] = True

    def add_prefix(self, data, reply):

        prefix_text = data.get('prefix_text', '')
        if not prefix_text:
            reply['success'] = False
            reply['msg'] = 'No prefix to add defined.'
            return

        if tp.is_maya():
            if prefix_text[0].isdigit():
                reply['success'] = False
                reply['msg'] = 'Maya does not supports names with digits as first character.'
                return

        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.add_name_prefix(
            prefix=prefix_text, filter_type=filter_type, search_hierarchy=search_hierarchy,
            selection_only=selection_only, rename_shape=rename_shape)

        reply['success'] = True

    def remove_prefix(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not search_hierarchy and not selection_only:
            LOGGER.warning('Remove prefix must be used with "Selected" options not with "All"')
            reply['success'] = False
            return

        tp.Dcc.remove_name_prefix(
            filter_type=filter_type, search_hierarchy=search_hierarchy,
            selection_only=selection_only, rename_shape=rename_shape)

        reply['success'] = True

    def remove_first(self, data, reply):
        num_to_remove = data.get('count', 0)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not num_to_remove > 0:
            LOGGER.warning('Specify a number of characters to remove greater than zero ({})'.format(num_to_remove))
            reply['success'] = False
            return

        if not search_hierarchy and not selection_only:
            LOGGER.warning('Remove first must be used with "Selected" options not with "All"')
            reply['success'] = False
            return

        filtered_obj_list = tp.Dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            original_name = tp.Dcc.node_short_name(obj)
            new_name = obj[num_to_remove + 1:]
            if not new_name:
                LOGGER.warning(
                    'Impossible to rename {}. Total characters to remove is greater or equal than '
                    'the original name length: {} >= {}'.format(original_name, num_to_remove, len(original_name)))
                continue
            tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)

        reply['success'] = True

    def add_suffix(self, data, reply):
        suffix_text = data.get('suffix_text', '')
        if not suffix_text:
            reply['success'] = False
            reply['msg'] = 'No suffix to add defined.'
            return

        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.add_name_suffix(
            suffix=suffix_text, filter_type=filter_type, search_hierarchy=search_hierarchy,
            selection_only=selection_only, rename_shape=rename_shape)

        reply['success'] = True

    def remove_suffix(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not search_hierarchy and not selection_only:
            msg = 'Remove suffix must be used with "Selected" options not with "All"'
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        tp.Dcc.remove_name_suffix(
            filter_type=filter_type, search_hierarchy=search_hierarchy,
            selection_only=selection_only, rename_shape=rename_shape)

        reply['success'] = True

    def remove_last(self, data, reply):
        num_to_remove = data.get('count', 0)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not num_to_remove > 0:
            msg = 'Specify a number of characters to remove greater than zero ({})'.format(num_to_remove)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        if not search_hierarchy and not selection_only:
            msg = 'Remove last must be used with "Selected" options not with "All"'
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        filtered_obj_list = tp.Dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            original_name = tp.Dcc.node_short_name(obj)
            new_name = obj[:-num_to_remove]
            if not new_name:
                LOGGER.warning(
                    'Impossible to rename {}. Total characters to remove is greater or equal than '
                    'the original name length: {} >= {}'.format(original_name, num_to_remove, len(original_name)))
                continue
            tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)

        reply['success'] = True

    def replace_padding(self, data, reply):
        pad = data.get('pad', 0)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not pad > 0:
            msg = 'Specify a padding greater than zero ({})'.format(pad)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        if not search_hierarchy and not selection_only:
            msg = 'Replace Padding must be used with "Selected" options not with "All"'
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        tp.Dcc.renumber_objects(
            filter_type=filter_type, remove_trailing_numbers=True, padding=int(pad), add_underscore=True,
            rename_shape=rename_shape, search_hierarchy=search_hierarchy, selection_only=selection_only
        )

        reply['success'] = True

    def append_padding(self, data, reply):
        pad = data.get('pad', 0)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not pad > 0:
            msg = 'Specify a padding greater than zero ({})'.format(pad)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        if not search_hierarchy and not selection_only:
            msg = 'Append Padding must be used with "Selected" options not with "All"'
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        tp.Dcc.renumber_objects(
            filter_type=filter_type, remove_trailing_numbers=False, padding=int(pad), add_underscore=True,
            rename_shape=rename_shape, search_hierarchy=search_hierarchy, selection_only=selection_only
        )

        reply['success'] = True

    def change_padding(self, data, reply):
        pad = data.get('pad', 0)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not pad > 0:
            msg = 'Specify a padding greater than zero ({})'.format(pad)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        if not search_hierarchy and not selection_only:
            msg = 'Change Padding must be used with "Selected" options not with "All"'
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        tp.Dcc.change_suffix_padding(
            filter_type=filter_type, padding=int(pad), add_underscore=True, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only
        )

        reply['success'] = True

    def add_side(self, data, reply):
        side = data.get('side', None)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not side:
            msg = 'Not side specified ({})'.format(side)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        tp.Dcc.add_name_suffix(
            suffix=side, filter_type=filter_type, add_underscore=True, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only
        )

        reply['success'] = True

    def add_replace_namespace(self, data, reply):
        namespace_to_add = data.get('namespace', None)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not namespace_to_add:
            msg = 'Not namespace specified ({})'.format(namespace_to_add)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        namespace.assign_namespace_to_object_by_filter(
            namespace=namespace_to_add, filter_type=filter_type, force_create=True, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only, dag=False, remove_maya_defaults=True,
            transforms_only=True)

        reply['success'] = True

    def remove_namespace(self, data, reply):
        namespace_to_remove = data.get('namespace', None)
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        if not namespace_to_remove:
            msg = 'Not namespace specified ({})'.format(namespace_to_remove)
            LOGGER.warning(msg)
            reply['success'] = False
            reply['msg'] = msg
            return

        namespace.remove_namespace_from_object_by_filter(
            namespace=namespace_to_remove, filter_type=filter_type, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only, dag=False, remove_maya_defaults=True,
            transforms_only=True)

        reply['success'] = True

    def search_and_replace(self, data, reply):
        search_str = data.get('search', '')
        replace_str = data.get('replace', '')
        nodes = data.get('nodes', list())
        if not nodes:
            nodes = tp.Dcc.selected_nodes()

        new_name = None
        for node in nodes:
            try:
                obj_short_name = tp.Dcc.node_short_name(node)
                new_name = obj_short_name.replace(search_str, replace_str)
                tp.Dcc.rename_node(node, new_name)
            except Exception as exc:
                LOGGER.warning('Impossible to rename {} >> {} | {}'.format(node, new_name, exc))

        reply['success'] = True

    def automatic_suffix(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.auto_name_suffix(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

        reply['success'] = True

    def make_unique_name(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.find_unique_name(
            filter_type=filter_type, do_rename=True, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

        reply['success'] = True

    def remove_all_numbers(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.remove_name_numbers(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only, trailing_only=False)

        reply['success'] = True

    def remove_trail_numbers(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        tp.Dcc.remove_name_numbers(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only, trailing_only=True)

        reply['success'] = True

    def clean_unused_namespaces(self, data, reply):
        namespace.remove_empty_namespaces()
        reply['success'] = True

    def open_namespace_editor(self, data, reply):
        gui.open_namespace_editor()
        reply['success'] = True

    def open_reference_editor(self, data, reply):
        gui.open_reference_editor()
        reply['success'] = True

    def rename(self):
        pass
