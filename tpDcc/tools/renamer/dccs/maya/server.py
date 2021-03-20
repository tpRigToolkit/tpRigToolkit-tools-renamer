#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tpDcc-tools-renamer server implementation for Maya
"""

from __future__ import print_function, division, absolute_import

import logging
from collections import OrderedDict

import maya.api.OpenMaya

from tpDcc import dcc
from tpDcc.core import server

from tpDcc.dccs.maya import api
from tpDcc.dccs.maya.core import namespace, gui

LOGGER = logging.getLogger('tpDcc-tools-renamer')


class RenamerServer(server.DccServer, object):
    PORT = 16231

    def simple_rename(self, data, reply):

        new_name = data.get('new_name', '')
        if not new_name:
            reply['msg'] = 'Please type a new name and try the operation again!'
            reply['success'] = False
            return

        rename_shape = data.get('rename_shape', True)
        nodes = data.get('nodes', list())
        if not nodes:
            nodes = dcc.selected_nodes()
        for node in nodes:
            dcc.rename_node(node, new_name, rename_shape=rename_shape)

        reply['success'] = True

    def find_auto_solved_data(self, data, reply):

        auto_rename_data = OrderedDict()

        auto_suffixes = data.get('auto_suffixes', dict())
        tokens_dict = data.get('tokens_dict', dict())
        last_joint_end = data.get('last_joint_end', True)
        nodes = data.get('nodes', list())
        if not nodes:
            nodes = dcc.selected_nodes()

        for i, obj_name in enumerate(reversed(nodes)):
            node_uuid = dcc.node_handle(obj_name)
            if node_uuid in auto_rename_data:
                LOGGER.warning(
                    'Node with name: "{} and UUID "{}" already renamed to "{}"! Skipping ...'.format(
                        obj_name, node_uuid, auto_rename_data[obj_name]))
                continue

            obj_type = dcc.object_type(obj_name)
            if obj_type == 'transform':
                shape_nodes = dcc.list_shapes(obj_name, full_path=True)
                if not shape_nodes:
                    obj_type = 'group'
                else:
                    obj_type = dcc.object_type(shape_nodes[0])
            elif obj_type == 'joint':
                shape_nodes = maya.cmds.listRelatives(obj_name, shapes=True, fullPath=True)
                if shape_nodes and maya.cmds.objectType(shape_nodes[0]) == 'nurbsCurve':
                    obj_type = 'controller'
                else:
                    children = dcc.list_children(obj_name)
                    if not children and last_joint_end:
                        obj_type = 'jointEnd'
            if obj_type == 'nurbsCurve':
                connections = maya.cmds.listConnections('{}.message'.format(obj_name))
                if connections:
                    for node in connections:
                        if maya.cmds.nodeType(node) == 'controller':
                            obj_type = 'controller'
                            break
            if obj_type not in auto_suffixes:
                node_type = obj_type
            else:
                node_type = auto_suffixes[obj_type]

            if 'node_type' in tokens_dict and tokens_dict['node_type']:
                node_type = tokens_dict.pop('node_type')
            node_name = dcc.node_short_name(obj_name)
            if 'description' in tokens_dict and tokens_dict['description']:
                description = tokens_dict['description']
            else:
                description = node_name

            auto_rename_data[node_uuid] = {'description': description, 'node_type': node_type}

        reply['success'] = True
        reply['result'] = auto_rename_data

    def add_prefix(self, data, reply):

        prefix_text = data.get('prefix_text', '')
        if not prefix_text:
            reply['success'] = False
            reply['msg'] = 'No prefix to add defined.'
            return

        if prefix_text[0].isdigit():
            reply['success'] = False
            reply['msg'] = 'Maya does not supports names with digits as first character.'
            return

        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        dcc.add_name_prefix(
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

        dcc.remove_name_prefix(
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

        filtered_obj_list = dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            original_name = dcc.node_short_name(obj)
            new_name = obj[num_to_remove + 1:]
            if not new_name:
                LOGGER.warning(
                    'Impossible to rename {}. Total characters to remove is greater or equal than '
                    'the original name length: {} >= {}'.format(original_name, num_to_remove, len(original_name)))
                continue
            dcc.rename_node(obj, new_name, rename_shape=rename_shape)

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

        dcc.add_name_suffix(
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

        dcc.remove_name_suffix(
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

        filtered_obj_list = dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            original_name = dcc.node_short_name(obj)
            new_name = obj[:-num_to_remove]
            if not new_name:
                LOGGER.warning(
                    'Impossible to rename {}. Total characters to remove is greater or equal than '
                    'the original name length: {} >= {}'.format(original_name, num_to_remove, len(original_name)))
                continue
            dcc.rename_node(obj, new_name, rename_shape=rename_shape)

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

        dcc.renumber_objects(
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

        dcc.renumber_objects(
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

        dcc.change_suffix_padding(
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

        dcc.add_name_suffix(
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
            nodes = dcc.selected_nodes()

        handles_list = list()
        for obj in nodes:
            sel = api.SelectionList()
            sel.add(obj)
            mobj = sel.get_depend_node(0)
            handle = maya.api.OpenMaya.MObjectHandle(mobj)
            handles_list.append(handle)

        new_name = None
        for node_handle in handles_list:
            node = node_handle
            try:
                mobj = node_handle.object()
                dag_path = maya.api.OpenMaya.MDagPath.getAPathTo(mobj)
                node = dag_path.partialPathName()
                obj_short_name = dag_path.partialPathName()
                new_name = obj_short_name.replace(search_str, replace_str)
                dcc.rename_node(node, new_name)
            except Exception as exc:
                LOGGER.warning('Impossible to rename {} >> {} | {}'.format(node, new_name, exc))

        reply['success'] = True

    def automatic_suffix(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        dcc.auto_name_suffix(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

        reply['success'] = True

    def make_unique_name(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        dcc.find_unique_name(
            filter_type=filter_type, do_rename=True, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

        reply['success'] = True

    def remove_all_numbers(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        dcc.remove_name_numbers(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only, trailing_only=False)

        reply['success'] = True

    def remove_trail_numbers(self, data, reply):
        rename_shape = data.get('rename_shape', True)
        search_hierarchy = data.get('hierarchy_check', False)
        selection_only = data.get('only_selection', True)
        filter_type = data.get('filter_type', None)

        dcc.remove_name_numbers(
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
