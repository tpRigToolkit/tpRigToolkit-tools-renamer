#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renamer widget controller class implementation
"""

from __future__ import print_function, division, absolute_import

import traceback

import tpDcc as tp
from tpDcc.libs.python import strings
from tpDcc.tools.renamer.core import utils

LOGGER = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


class RenamerController(object):
    def __init__(self, client, model):
        super(RenamerController, self).__init__()

        self._client = client
        self._model = model

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

        if tp.is_maya():
            import tpDcc.dccs.maya as maya

        for item in items:
            compare_item = item
            if not text:
                base_name = None
                if tp.is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
                            base_name = dag_path.partialPathName()
                            compare_item = base_name
                        except Exception as exc:
                            LOGGER.warning('Error while retrieving node path from MObject: {}'.format(exc))
                            continue
                if base_name is None:
                    if hasattr(item, 'obj'):
                        base_name = item.obj
                    else:
                        base_name = tp.Dcc.node_short_name(item)
            else:
                base_name = text
                if tp.is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
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

            if not isinstance(item, (str, unicode)) and hasattr(item, 'preview_name'):
                item.preview_name = preview_name

            generated_names.append(preview_name)

        return generated_names

    @tp.Dcc.get_undo_decorator()
    def rename(self, **kwargs):
        hierarchy_check = self._model.hierarchy_check
        selection_type = self._model.selection_type

        nodes = utils.get_objects_to_rename(hierarchy_check=hierarchy_check, selection_type=selection_type, uuid=True)
        generated_names = self.generate_names(items=nodes, **kwargs)

        if not generated_names or len(nodes) != len(generated_names):
            LOGGER.warning('Impossible to rename because was impossible to generate some of the names ...')
            return

        if tp.is_maya():
            import tpDcc.dccs.maya as maya

        for item, new_name in zip(nodes, generated_names):
            if tp.is_maya():
                mobj = None
                if hasattr(item, 'handle'):
                    mobj = item.handle.object()
                elif hasattr(item, 'object'):
                    mobj = item.object()
                if mobj:
                    try:
                        dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
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
                tp.Dcc.rename_node(full_name, new_name)
                if hasattr(item, 'obj') and hasattr(item, 'preview_name'):
                    item.obj = item.preview_name
                    item.preview_name = ''
            except Exception:
                LOGGER.error('Impossible to rename: {} to {} | {}'.format(full_name, new_name, traceback.format_exc()))

    def _find_manual_available_name(
            self, items, name, prefix=None, suffix=None, side='', index=-1, padding=0, letters=False, capital=False,
            remove_first=0, remove_last=0, search_str=None, replace_str=None, joint_end=False):

        if tp.is_maya():
            import tpDcc.dccs.maya as maya

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
                if tp.is_maya():
                    if hasattr(item, 'object'):
                        mobj = item.object()
                        try:
                            dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
                            item_to_add = dag_path.partialPathName()
                            item_names.append(item_to_add)
                            continue
                        except Exception as exc:
                            LOGGER.warning('Error while retrieving node path from MObject: {}'.format(exc))
                            continue
                else:
                    item_names.append(item)

        # if object exists, try next index
        if tp.Dcc.object_exists(test_name) or test_name in item_names:
            new_index = int(index) + 1
            return self._find_manual_available_name(
                items, name, prefix=prefix, index=new_index, padding=padding,
                letters=letters, capital=capital, remove_first=remove_first, remove_last=remove_last,
                joint_end=joint_end, search_str=search_str, replace_str=replace_str
            )

        return test_name
