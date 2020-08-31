#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages utils rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import dividers


class UtilsView(base.BaseWidget, object):
    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(UtilsView, self).__init__(parent=parent)

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(UtilsView, self).ui()

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(2)
        self.main_layout.addLayout(base_layout)

        name_utils_layout = QHBoxLayout()
        name_utils_layout.setContentsMargins(0, 0, 0, 0)
        name_utils_layout.setSpacing(5)
        self._automatic_suffix_btn = QPushButton('Automatic Suffix')
        self._automatic_suffix_btn.setIcon(tp.ResourcesMgr().icon('suffix'))
        self._make_unique_name_btn = QPushButton('Make Unique Name')
        self._make_unique_name_btn.setIcon(tp.ResourcesMgr().icon('name'))
        name_utils_layout.addWidget(self._automatic_suffix_btn)
        name_utils_layout.addWidget(self._make_unique_name_btn)

        if tp.is_maya():
            namespace_utils_layout = QHBoxLayout()
            namespace_utils_layout.setContentsMargins(0, 0, 0, 0)
            namespace_utils_layout.setSpacing(5)
            self._clean_unused_namespaces_btn = QPushButton('Unused Namespaces')
            self._clean_unused_namespaces_btn.setIcon(tp.ResourcesMgr().icon('clean'))
            self._namespace_editor_btn = QPushButton('Namespace Editor')
            self._namespace_editor_btn.setIcon(tp.ResourcesMgr().icon('browse_page'))
            self._reference_editor_btn = QPushButton('Reference Editor')
            self._reference_editor_btn.setIcon(tp.ResourcesMgr().icon('connect'))
            namespace_utils_layout.addWidget(self._clean_unused_namespaces_btn)
            namespace_utils_layout.addWidget(self._namespace_editor_btn)
            namespace_utils_layout.addWidget(self._reference_editor_btn)

        index_utils_layout = QHBoxLayout()
        index_utils_layout.setContentsMargins(0, 0, 0, 0)
        index_utils_layout.setSpacing(5)
        self._remove_all_numbers_btn = QPushButton('Remove All Numbers')
        self._remove_all_numbers_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        self._remove_tail_numbers_btn = QPushButton('Remove Tail Numbers')
        self._remove_tail_numbers_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        index_utils_layout.addWidget(self._remove_all_numbers_btn)
        index_utils_layout.addWidget(self._remove_tail_numbers_btn)

        base_layout.addLayout(name_utils_layout)
        base_layout.addLayout(dividers.DividerLayout())
        base_layout.addLayout(index_utils_layout)
        if tp.is_maya():
            base_layout.addLayout(dividers.DividerLayout())
            base_layout.addLayout(namespace_utils_layout)

    def setup_signals(self):
        self._automatic_suffix_btn.clicked.connect(self._controller.automatic_suffix)
        self._make_unique_name_btn.clicked.connect(self._controller.make_unique_name)
        self._remove_all_numbers_btn.clicked.connect(self._controller.remove_all_numbers)
        self._remove_tail_numbers_btn.clicked.connect(self._controller.remove_trail_numbers)
        if tp.is_maya():
            self._clean_unused_namespaces_btn.clicked.connect(self._controller.clean_unused_namespaces)
            self._namespace_editor_btn.clicked.connect(self._controller.open_namespace_editor)
            self._reference_editor_btn.clicked.connect(self._controller.open_reference_editor)


class UtilsWidgetModel(QObject, object):
    def __init__(self):
        super(UtilsWidgetModel, self).__init__()

        self._global_data = dict()

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict


class UtilsWidgetController(object):
    def __init__(self, client, model):
        super(UtilsWidgetController, self).__init__()

        self._client = client
        self._model = model

    @tp.Dcc.get_undo_decorator()
    def automatic_suffix(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.automatic_suffix(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def make_unique_name(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.make_unique_name(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_all_numbers(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_all_numbers(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_trail_numbers(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_trail_numbers(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def clean_unused_namespaces(self):
        return self._client.clean_unused_namespaces()

    def open_namespace_editor(self):
        return self._client.open_namespace_editor()

    def open_reference_editor(self):
        return self._client.open_reference_editor()


def utils_widget(client, parent=None):

    model = UtilsWidgetModel()
    controller = UtilsWidgetController(client=client, model=model)
    view = UtilsView(model=model, controller=controller, parent=parent)

    return view
