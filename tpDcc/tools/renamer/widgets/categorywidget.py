#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains category widget implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import search, buttons, splitters

if tp.is_maya():
    import tpDcc.dccs.maya as maya


class CategoryWidget(base.BaseWidget, object):

    doRefresh = Signal(object)
    doPreview = Signal(list, bool)
    doRename = Signal()
    togglePreview = Signal()

    def __init__(self, types, nodes_to_discard=None, parent=None):
        self._types = types
        self._default_nodes_to_discard = nodes_to_discard or list()
        self._category_buttons = list()
        super(CategoryWidget, self).__init__(parent=parent)

    @property
    def types(self):
        return self._types

    @property
    def nodes_to_discard(self):
        return self._default_nodes_to_discard

    @nodes_to_discard.setter
    def nodes_to_discard(self, nodes_to_discard):
        self._default_nodes_to_discard = nodes_to_discard

    def ui(self):
        super(CategoryWidget, self).ui()

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(10, 0, 10, 0)
        filter_layout.setSpacing(2)
        self.main_layout.addLayout(filter_layout)
        refresh_icon = tp.ResourcesMgr().icon('refresh')
        self._refresh_list_btn = buttons.IconButton(
            icon=refresh_icon, icon_padding=2, button_style=buttons.ButtonStyles.FlatStyle)
        self._names_filter = search.SearchFindWidget()
        self._search_lbl = QLabel('0 found')
        filter_layout.addWidget(self._refresh_list_btn)
        filter_layout.addWidget(self._names_filter)
        filter_layout.addWidget(self._search_lbl)

        self._types_layout = QHBoxLayout()
        self._types_layout.setContentsMargins(0, 0, 0, 0)
        self._types_layout.setSpacing(2)
        self.main_layout.addLayout(self._types_layout)

        self._names_list = QTreeWidget(self)
        self._names_list.setHeaderHidden(True)
        self._names_list.setSortingEnabled(False)
        self._names_list.setRootIsDecorated(False)
        self._names_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._names_list.sortByColumn(0, Qt.AscendingOrder)
        self._names_list.setUniformRowHeights(True)
        self._names_list.setAlternatingRowColors(True)

        self.main_layout.addWidget(self._names_list)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setAlignment(Qt.AlignLeft)
        bottom_buttons_layout.setContentsMargins(2, 2, 2, 2)
        bottom_buttons_layout.setSpacing(2)
        self.main_layout.addLayout(bottom_buttons_layout)

        preview_icon = tp.ResourcesMgr().icon('preview')
        self._sort_btn = QPushButton('Sort')
        self._sort_btn.setMinimumWidth(40)
        self._all_btn = QPushButton('All')
        self._all_btn.setMinimumWidth(40)
        self._none_btn = QPushButton('None')
        self._none_btn.setMinimumWidth(40)
        bottom_buttons_layout.addWidget(self._sort_btn)
        bottom_buttons_layout.addWidget(self._all_btn)
        bottom_buttons_layout.addWidget(self._none_btn)

        bottom_buttons_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._hide_default_scene_nodes_cbx = QCheckBox('Hide Default Scene Objects')
        self._hide_default_scene_nodes_cbx.setChecked(True)
        bottom_buttons_layout.addWidget(self._hide_default_scene_nodes_cbx)

        self.main_layout.addLayout(splitters.SplitterLayout())

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(2)
        self.main_layout.addLayout(preview_layout)

        self._preview_btn = QPushButton('Preview')
        self._preview_btn.setIcon(preview_icon)
        self._preview_btn.setCheckable(True)
        self._preview_btn.setChecked(True)
        self._preview_btn.setMinimumWidth(100)
        self._preview_btn.setMaximumWidth(100)
        self._rename_btn = QPushButton('Select objects in the list to rename ...')
        self._rename_btn.setEnabled(False)
        preview_layout.addWidget(self._preview_btn)
        preview_layout.addWidget(self._rename_btn)

        self._setup_types()
        self.refresh()

    def setup_signals(self):
        self._refresh_list_btn.clicked.connect(self._on_refresh_list)
        self._names_filter.textChanged.connect(self._on_filter_names_changed)
        self._hide_default_scene_nodes_cbx.toggled.connect(self._on_toggle_hide_default_scene_nodes_cbx)
        self._names_list.itemSelectionChanged.connect(self._on_item_selection_changed)
        self._none_btn.clicked.connect(self._on_select_none_clicked)
        self._all_btn.clicked.connect(self._on_select_all_clicked)
        self._preview_btn.toggled.connect(self._on_toggle_preview)
        self._rename_btn.clicked.connect(self.doRename.emit)

    def get_names_list(self):
        return self._names_list

    def is_preview_enabled(self):
        return self._preview_btn.isChecked()

    def refresh(self, selected_objects=False, hierarchy=False):
        self._names_list.clear()
        self._names_list.setSortingEnabled(True)

        try:
            objs_names = list()
            if not selected_objects:
                objs_names.extend(tp.Dcc.all_scene_objects(full_path=True))
            else:
                objs_names.extend(tp.Dcc.selected_nodes(full_path=True))
                if objs_names and hierarchy:
                    children_list = list()
                    for obj in objs_names:
                        children = tp.Dcc.list_children(obj, all_hierarchy=True, full_path=True)
                        if children:
                            children_list.extend(children)
                    children_list = list(set(children_list))
                    objs_names.extend(children_list)
            self._update_names_list(objs_names)
            self._on_filter_names_changed(self._names_filter.get_text())
        finally:
            self._names_list.setSortingEnabled(False)

    def _setup_types(self):
        for i, category_type in enumerate(self._types):
            for type_name, type_data in category_type.items():
                dcc_type = type_data.get('type', None)
                dcc_fn = type_data.get('fn', None)
                dcc_args = type_data.get('args', dict())
                type_btn = QPushButton(type_name)
                type_btn.setCheckable(True)
                type_btn.setProperty('dcc_type', dcc_type)
                type_btn.setProperty('dcc_fn', dcc_fn)
                type_btn.setProperty('dcc_args', dcc_args)
                if i == 0:
                    type_btn.setChecked(True)
                self._types_layout.addWidget(type_btn)
                self._category_buttons.append(type_btn)
                type_btn.toggled.connect(self._on_toggle_type)

        self._others_btn = QPushButton('Others')
        self._others_btn.setCheckable(True)
        self._types_layout.addWidget(self._others_btn)
        self._others_btn.toggled.connect(self._on_toggle_type)

    def _get_nodes_to_discard(self):
        """
        Internal function that returns list of nodes that should be discarded during renaming process
        """

        discard_nodes = self._default_nodes_to_discard[:] or list()

        if self._hide_default_scene_nodes_cbx and self._hide_default_scene_nodes_cbx.isChecked():
            discard_nodes.extend(tp.Dcc.default_scene_nodes(full_path=False))

        # discard_nodes.extend(tp.Dcc.list_nodes(node_type='camera'))

        for btn in self._category_buttons:
            if not btn.isChecked():
                dcc_type = btn.property('dcc_type')
                if dcc_type:
                    discard_nodes.extend(tp.Dcc.list_nodes(node_type=btn.property('dcc_type')))
                else:
                    dcc_fn = btn.property('dcc_fn')
                    if dcc_fn:
                        dcc_args = btn.property('dcc_args')
                        if tp.is_maya():
                            valid_args = dict()
                            for arg_name, arg_value in dcc_args.items():
                                valid_args[str(arg_name)] = arg_value
                            nodes = getattr(maya.cmds, dcc_fn)(**valid_args)
                            discard_nodes.extend(nodes)

        return list(set(discard_nodes))

    def _get_node_types(self):
        node_types = set()
        for btn in self._category_buttons:
            dcc_type = btn.property('dcc_type')
            if dcc_type:
                node_types.add(dcc_type)
            else:
                dcc_fn = btn.property('dcc_fn')
                if dcc_fn:
                    dcc_args = btn.property('dcc_args')
                    if tp.is_maya():
                        valid_args = dict()
                        for arg_name, arg_value in dcc_args.items():
                            valid_args[str(arg_name)] = arg_value
                        nodes = getattr(maya.cmds, dcc_fn)(**valid_args)
                        for node in nodes:
                            node_type = tp.Dcc.node_type(node)
                            node_types.add(node_type)

        return list(node_types)

    def _update_names_list(self, nodes):
        """
        Internal function that updates names list with given node names
        :param nodes: list(str)
        """

        nodes_to_discard = self._get_nodes_to_discard() or list()

        nodes = list(set(nodes))

        for obj in nodes:
            if obj in nodes_to_discard:
                continue
            node_type = tp.Dcc.node_type(obj)
            if node_type not in self._get_node_types() and not self._others_btn.isChecked():
                is_valid = False
                for node_type in self._get_node_types():
                    is_valid = tp.Dcc.check_object_type(obj, node_type, check_sub_types=True)
                    if is_valid:
                        break
                if not is_valid:
                    continue

            node_name = tp.Dcc.node_short_name(obj)
            item = QTreeWidgetItem(self._names_list, [node_name])
            item.obj = node_name
            item.preview_name = ''
            item.full_name = obj
            if tp.is_maya():
                mobj = maya.OpenMaya.MObject()
                sel = maya.OpenMaya.MSelectionList()
                sel.add(obj)
                sel.getDependNode(0, mobj)
                item.handle = maya.OpenMaya.MObjectHandle(mobj)

            self._names_list.addTopLevelItem(item)

    def _on_filter_names_changed(self, filter_text):
        """
        Internal callback function that is called each time the user enters text in the search line widget
        Shows or hides elements in the list taking in account the filter_text
        :param filter_text: str, current text
        """

        nodes_found = 0
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            # item.setHidden(filter_text not in item.text(0))
            if filter_text not in item.text(0):
                item.setHidden(True)
            else:
                item.setHidden(False)
                nodes_found += 1

        if filter_text:
            self._search_lbl.setText('{} found'.format(nodes_found))
        else:
            self._search_lbl.setText('0 found')

    def _on_item_selection_changed(self):
        """
        Internal callback function that is triggered when the user selects an item in the names list
        """

        selected_items = self._names_list.selectedItems()
        item_names = [item.obj for item in selected_items]
        if len(selected_items) > 0:
            self._rename_btn.setText('Rename')
            self._rename_btn.setEnabled(True)
        else:
            self._rename_btn.setText('Select objects in the list to rename ...')
            self._rename_btn.setEnabled(False)

        # We reset name to original value
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            if item.text(0) in item_names:
                continue
            if hasattr(item, 'obj'):
                item.setText(0, item.obj)

        self.doPreview.emit(selected_items, self._preview_btn.isChecked())

    def _on_select_all_clicked(self):
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            item.setSelected(True)

    def _on_select_none_clicked(self):
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            item.setSelected(False)

    def _on_refresh_list(self):
        self.doRefresh.emit(self)

    def _on_toggle_type(self, flag):
        self.doRefresh.emit(self)

    def _on_toggle_hide_default_scene_nodes_cbx(self, flag):
        self.doRefresh.emit(self)

    def _on_toggle_preview(self, flag):
        self.togglePreview.emit()


