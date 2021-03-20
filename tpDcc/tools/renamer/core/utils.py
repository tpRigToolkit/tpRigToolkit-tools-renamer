#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions for renamer tool
"""

from __future__ import print_function, division, absolute_import

import logging

from tpDcc import dcc

from tpDcc.tools.renamer.core import consts

LOGGER = logging.getLogger('tpDcc-tools-renamer')


def get_objects_to_rename(hierarchy_check, selection_type, uuid=False):
    search_hierarchy = hierarchy_check
    search_selection = True if selection_type == 0 else False

    if not search_selection:
        objs_to_rename = dcc.client(consts.TOOL_ID).all_scene_nodes(full_path=True)
    else:
        objs_to_rename = dcc.client(consts.TOOL_ID).selected_nodes(full_path=True)

    if not objs_to_rename:
        LOGGER.warning('No objects to rename!')
        return

    if search_hierarchy:
        children_list = list()
        for obj in objs_to_rename:
            children = dcc.client(consts.TOOL_ID).list_children(obj, all_hierarchy=True, full_path=True)
            if children:
                children_list.extend(children)
        children_list = list(set(children_list))
        objs_to_rename.extend(children_list)

    if uuid and dcc.client(consts.TOOL_ID).is_maya():
        import tpDcc.dccs.maya as maya

        handles_list = list()
        # objs_to_rename = [obj for obj in objs_to_rename if dcc.node_type(obj) == 'transform']
        for obj in objs_to_rename:
            mobj = maya.OpenMaya.MObject()
            sel = maya.OpenMaya.MSelectionList()
            sel.add(obj)
            sel.getDependNode(0, mobj)
            handle = maya.OpenMaya.MObjectHandle(mobj)
            handles_list.append(handle)
        return handles_list
    else:
        # We reverse the list so we update first children and later parents, otherwise we will have
        # problems during renaming if we use full paths
        objs_to_rename.reverse()

    return objs_to_rename
