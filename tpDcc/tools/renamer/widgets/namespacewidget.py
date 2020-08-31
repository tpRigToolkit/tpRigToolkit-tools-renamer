#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages namespace rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base

from tpDcc.libs.qt.widgets import layouts, checkbox, lineedit, combobox, buttons


class NamespaceView(base.BaseWidget, object):

    # renameUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(NamespaceView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(NamespaceView, self).ui()

        namespace_layout = layouts.HorizontalLayout(spacing=5, margins=(0, 0, 0, 0))
        namespace_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(namespace_layout)
        self._namespace_cbx = checkbox.BaseCheckBox(parent=self)
        self._namespace_line = lineedit.BaseLineEdit(parent=self)
        self._namespace_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._namespace_line.setPlaceholderText('Namespace')
        self._namespace_combo = combobox.BaseComboBox(parent=self)
        self._namespace_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._combo_icons = [tp.ResourcesMgr().icon('add'), tp.ResourcesMgr().icon('trash')]
        self._namespace_btn = buttons.BaseButton(parent=self)
        self._namespace_btn.setIcon(self._combo_icons[0])
        namespace_layout.addWidget(self._namespace_cbx)
        namespace_layout.addWidget(self._namespace_line)
        namespace_layout.addWidget(self._namespace_combo)
        namespace_layout.addWidget(self._namespace_btn)

    def setup_signals(self):
        self._namespace_combo.currentIndexChanged.connect(self._on_combo_index_changed)

        self._namespace_cbx.toggled.connect(self._controller.toggle_namespace)
        self._namespace_line.textChanged.connect(self._controller.change_namespace)
        self._namespace_combo.currentIndexChanged.connect(self._controller.change_namespace_option)
        self._namespace_btn.clicked.connect(self._controller.update_namespace)

        self._model.namespaceCheckChanged.connect(self._on_namespace_toggled)
        self._model.namespaceChanged.connect(self._namespace_line.setText)
        self._model.namespaceOptionChanged.connect(self._namespace_combo.setCurrentIndex)

    def refresh(self):
        self._namespace_combo.clear()
        self._namespace_combo.addItems(['Add/Replace', 'Remove'])
        self._namespace_cbx.setChecked(self._model.namespace_check)
        self._namespace_line.setText(self._model.namespace)
        self._namespace_combo.setCurrentIndex(self._model.namespace_option)
        # self.renameUpdate.emit()

    def _on_namespace_toggled(self, flag):
        self._namespace_cbx.setChecked(flag)
        self._namespace_line.setEnabled(flag)
        self._namespace_combo.setEnabled(flag)
        self._namespace_btn.setEnabled(flag)
        # self.renameUpdate.emit()

    def _on_combo_index_changed(self, index):
        """
        Internal callback function that is called when the user selects a new index in namespace combo
        :param index: int
        """

        self._namespace_btn.setIcon(self._combo_icons[index])
        # self.renameUpdate.emit()


class NamespaceWidgetModel(QObject, object):
    namespaceCheckChanged = Signal(bool)
    namespaceChanged = Signal(str)
    namespaceOptionChanged = Signal(int)

    def __init__(self):
        super(NamespaceWidgetModel, self).__init__()

        self._global_data = dict()
        self._namespace_check = True
        self._namespace = ''
        self._namespace_option = 0

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict

    @property
    def namespace_check(self):
        return self._namespace_check

    @namespace_check.setter
    def namespace_check(self, flag):
        self._namespace_check = bool(flag)
        self.namespaceCheckChanged.emit(self._namespace_check)

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, value):
        self._namespace = str(value)
        self.namespaceChanged.emit(self._namespace)

    @property
    def namespace_option(self):
        return self._namespace_option

    @namespace_option.setter
    def namespace_option(self, value):
        self._namespace_option = int(value)
        self.namespaceOptionChanged.emit(self._namespace_option)

    @property
    def rename_settings(self):
        namespace = self.namespace if self.namespace_check else ''
        namespace_option = self.namespace_option

        return {
            'namespace': namespace,
            'namespace_option': namespace_option
        }


class NamespaceWidgetController(object):
    def __init__(self, client, model):
        super(NamespaceWidgetController, self).__init__()

        self._client = client
        self._model = model

    def toggle_namespace(self, flag):
        self._model.namespace_check = flag

    def change_namespace(self, value):
        self._model.namespace = value

    def change_namespace_option(self, value):
        self._model.namespace_option = value

    def update_namespace(self):
        namespace_text = self._model.namespace
        if not namespace_text:
            return

        namespace_option = self._model.namespace_option

        if namespace_option == 0:
            self.add_replace_namespace()
        elif namespace_option == 1:
            self.remove_namespace()

    @tp.Dcc.get_undo_decorator()
    def add_replace_namespace(self):
        global_data = self._model.global_data
        namespace = self._model.namespace
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.add_replace_namespace(
            namespace=namespace, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_namespace(self):
        global_data = self._model.global_data
        namespace = self._model.namespace
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_namespace(
            namespace=namespace, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )


def namespace_widget(client, parent=None):
    model = NamespaceWidgetModel()
    controller = NamespaceWidgetController(client=client, model=model)
    view = NamespaceView(model=model, controller=controller, parent=parent)

    return view
