#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renamer widget controller class implementation
"""

from __future__ import print_function, division, absolute_import

import logging
import traceback
from collections import OrderedDict
from tpDcc import dcc
from tpDcc.libs.python import python, strings
from tpDcc.tools.renamer.core import utils

LOGGER = logging.getLogger('tpDcc-tools-renamer')


class RenamerController(object):
    def __init__(self, naming_lib, client, model):
        super(RenamerController, self).__init__()

        self._client = client
        self._model = model
        self._naming_lib = naming_lib

    @property
    def naming_lib(self):
        return self._naming_lib

    @property
    def client(self):
        return self._client

    @property
    def model(self):
        return self._model

    def set_selected(self):
        self._model.selection_type = 0

    def set_all_selection(self):
        self._model.selection_type = 1

    def set_filter_type(self, value):
        self._model.filter_type = value

    def hierarchy_check_toggle(self, flag):
        self._model.hierarchy_check = flag

    def auto_rename_shapes_check_toggle(self, flag):
        self._model.rename_shape = flag

    def generate_names(self, items, **kwargs):
        text = kwargs.get('name', '')
        prefix = kwargs.get('prefix', '')
        suffix = kwargs.get('suffix', '')
        padding = kwargs.get('padding', 0)
        naming_method = kwargs.get('naming_method', 0)
        upper = kwargs.get('upper', False)
        side = kwargs.get('side', '')
        remove_first = kwargs.get('remove_first', 0)
        remove_last = kwargs.get('remove_last', 0)
        joint_end = kwargs.get('joint_end', False)
        search_str = kwargs.get('search', '')
        replace_str = kwargs.get('replace', '')

        duplicated_names = dict()
        generated_names = list()

        for item in items:
            compare_item = item
            if not text:
                base_name = None
                if dcc.client().is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.api.OpenMaya.MDagPath.getAPathTo(mobj)
                            base_name = dag_path.partialPathName()
                            compare_item = base_name
                        except Exception as exc:
                            LOGGER.warning('Error while retrieving node path from MObject: {}'.format(exc))
                            continue
                if base_name is None:
                    if hasattr(item, 'obj'):
                        base_name = item.obj
                    else:
                        base_name = dcc.node_short_name(item)
            else:
                base_name = text
                if dcc.client().is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.api.OpenMaya.MDagPath.getAPathTo(mobj)
                            compare_item = dag_path.partialPathName()
                        except Exception as exc:
                            LOGGER.warning('Error while retrieving node path from MObject: {}'.format(exc))
                            continue

            if base_name == compare_item and not prefix and not suffix and not side:
                generate_preview_name = False
            else:
                generate_preview_name = True
            if base_name in duplicated_names:
                duplicated_names[base_name] += 1
            else:
                duplicated_names[base_name] = 0

            if generate_preview_name:
                if base_name == compare_item and (prefix or suffix or side):
                    index = None
                else:
                    index = duplicated_names[base_name]
                preview_name = self._find_manual_available_name(
                    items, base_name, prefix=prefix, side=side, suffix=suffix, index=index, padding=padding,
                    letters=naming_method, capital=upper, joint_end=joint_end, remove_first=remove_first,
                    remove_last=remove_last, search_str=search_str, replace_str=replace_str)
                while preview_name in generated_names:
                    duplicated_names[base_name] += 1
                    preview_name = self._find_manual_available_name(
                        items, base_name, prefix=prefix, side=side, suffix=suffix, index=duplicated_names[base_name],
                        padding=padding, letters=naming_method, capital=upper, joint_end=joint_end,
                        remove_first=remove_first, remove_last=remove_last, search_str=search_str,
                        replace_str=replace_str)
            else:
                preview_name = base_name

            if not python.is_string(item) and hasattr(item, 'preview_name'):
                item.preview_name = preview_name

            generated_names.append(preview_name)

        return generated_names

    def set_naming_file(self, file_path):
        self._naming_lib.naming_file = file_path
        self.update_rules()

    def update_rules(self):
        if not self._naming_lib:
            return list()

        self._model.rules = self._naming_lib.rules
        self._model.active_rule = self._naming_lib.active_rule()
        self._model.tokens = self._naming_lib.tokens

    def change_unique_id_auto(self, flag):
        self._model.unique_id_auto = flag

    def change_last_joint_end_auto(self, flag):
        self._model.last_joint_end_auto = flag

    def change_selected_rule(self, active_rule):
        self._model.active_rule = active_rule

    @dcc.undo_decorator()
    def auto_rename(self, tokens_dict, unique_id=True, last_joint_end=True):
        active_rule = self._model.active_rule
        if not active_rule:
            LOGGER.warning('Impossible to auto rename because no active rule defined.')
            return False

        rule_name = active_rule.name

        hierarchy_check = self._model.hierarchy_check
        selection_type = self._model.selection_type
        rename_shape = self._model.rename_shape

        if not self._naming_lib.has_rule(rule_name):
            return False

        current_rule = self._naming_lib.active_rule()

        self._naming_lib.set_active_rule(rule_name)

        objs_to_rename = utils.get_objects_to_rename(
            hierarchy_check=hierarchy_check, selection_type=selection_type, uuid=False) or list()
        if not objs_to_rename:
            LOGGER.warning('No objects to rename. Please select at least one object!')
            return False

        auto_suffixes = None
        if self._model.naming_config:
            auto_suffixes_data = self._model.naming_config.get('auto_suffixes', default=dict())
            if auto_suffixes_data:
                auto_suffixes = auto_suffixes_data.get(rule_name, None)

        solved_names = OrderedDict()
        if auto_suffixes:
            auto_data = self._client.find_auto_solved_data(
                auto_suffixes=auto_suffixes, tokens_dict=tokens_dict, last_joint_end=last_joint_end,
                nodes=objs_to_rename)

            for i, (node_uuid, data) in enumerate(auto_data.items()):
                description = data.get('description', '')
                side = tokens_dict.get('side', None)
                node_type = data.get('node_type', '')
                if unique_id:
                    solved_name = self._naming_lib.solve(description, side=side, node_type=node_type, id=i)
                else:
                    solved_name = self._naming_lib.solve(description, side=side, node_type=node_type)
                if not solved_name:
                    continue
                solved_name = self._client.find_unique_name(solved_name)
                solved_names[node_uuid] = solved_name

        if solved_names:
            for obj_id, solved_name in solved_names.items():
                obj_name = self._client.find_node_by_id(unique_id=obj_id, full_path=True)
                if not obj_name:
                    LOGGER.warning('Was not possible to find a node from UUID "{}" in current scene'.format(obj_id))
                    continue
                self._client.rename_node(obj_name, solved_name, uuid=obj_id, rename_shape=rename_shape)
        else:
            for obj_name in objs_to_rename:
                solve_name = self._naming_lib.solve(**tokens_dict)
                if not solve_name:
                    LOGGER.warning(
                        'Impossible to rename "{}" with rule "{}" | "{}"'.format(obj_name, rule_name, tokens_dict))
                    continue
                try:
                    self._client.rename_node(obj_name, solve_name, rename_shape=rename_shape)
                except Exception as exc:
                    LOGGER.error('Impossible to rename "{}" to "{}" | {}'.format(obj_name, solve_name, exc))
                    continue

        if current_rule:
            self._naming_lib.set_active_rule(current_rule.name)

    @dcc.undo_decorator()
    def rename(self, **kwargs):
        hierarchy_check = self._model.hierarchy_check
        selection_type = self._model.selection_type

        nodes = utils.get_objects_to_rename(hierarchy_check=hierarchy_check, selection_type=selection_type, uuid=True)
        generated_names = self.generate_names(items=nodes, **kwargs)

        if not generated_names or len(nodes) != len(generated_names):
            LOGGER.warning('Impossible to rename because was impossible to generate some of the names ...')
            return

        if dcc.is_maya():
            import maya.api.OpenMaya

        for item, new_name in zip(nodes, generated_names):
            if dcc.is_maya():
                mobj = None
                if hasattr(item, 'handle'):
                    mobj = item.handle.object()
                elif hasattr(item, 'object'):
                    mobj = item.object()
                if mobj:
                    try:
                        dag_path = maya.api.OpenMaya.MDagPath.getAPathTo(mobj)
                        full_name = dag_path.fullPathName()
                    except Exception as exc:
                        if hasattr(item, 'full_name'):
                            full_name = item.full_name
                        else:
                            LOGGER.warning('Impossible to retrieve Maya node full path: {}'.format(item))
                            continue
                else:
                    full_name = item
            else:
                if hasattr(item, 'full_name'):
                    full_name = item.full_name
                else:
                    full_name = item

            try:
                dcc.rename_node(full_name, new_name)
                if hasattr(item, 'obj') and hasattr(item, 'preview_name'):
                    item.obj = item.preview_name
                    item.preview_name = ''
            except Exception:
                LOGGER.error('Impossible to rename: {} to {} | {}'.format(full_name, new_name, traceback.format_exc()))

    def _find_manual_available_name(
            self, items, name, prefix=None, suffix=None, side='', index=-1, padding=0, letters=False, capital=False,
            remove_first=0, remove_last=0, search_str=None, replace_str=None, joint_end=False):

        if dcc.is_maya():
            import maya.api.OpenMaya

        if prefix:
            if side and side != '':
                test_name = '{}_{}_{}'.format(prefix, side, name)
            else:
                test_name = '{}_{}'.format(prefix, name)
        else:
            if side and side != '':
                test_name = '{}_{}'.format(side, name)
            else:
                test_name = name

        if index >= 0:
            if letters:
                letter = strings.get_alpha(index, capital)
                test_name = '{}_{}'.format(test_name, letter)
            else:
                test_name = '{}_{}'.format(test_name, str(index).zfill(padding))

        if suffix:
            test_name = '{}_{}'.format(test_name, suffix)

        if remove_first and remove_first > 0:
            test_name = test_name[remove_first:]

        if remove_last and remove_last > 0:
            test_name = test_name[:-remove_last]

        if search_str is not None and search_str != '' and replace_str is not None:
            test_name = test_name.replace(search_str, replace_str)

        item_names = list()
        for item in items:
            if hasattr(item, 'obj'):
                item_names.append(item.obj)
            else:
                if dcc.is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.api.OpenMaya.MDagPath.getAPathTo(mobj)
                            item_to_add = dag_path.partialPathName()
                            item_names.append(item_to_add)
                            continue
                        except Exception as exc:
                            LOGGER.warning('Error while retrieving node path from MObject: {}'.format(exc))
                            continue
                else:
                    item_names.append(item)

        # if object exists, try next index
        if dcc.node_exists(test_name) or test_name in item_names:
            new_index = int(index) + 1
            return self._find_manual_available_name(
                items, name, prefix=prefix, index=new_index, padding=padding,
                letters=letters, capital=capital, remove_first=remove_first, remove_last=remove_last,
                joint_end=joint_end, search_str=search_str, replace_str=replace_str
            )

        return test_name
