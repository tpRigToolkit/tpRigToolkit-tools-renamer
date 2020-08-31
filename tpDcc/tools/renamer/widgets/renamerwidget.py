#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages basic rename functionality for tpDcc-tools-renamer
"""

from __future__ import print_function, division, absolute_import


from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, dividers, buttons, checkbox, lineedit

from tpDcc.tools.renamer.core import utils


class RenamerView(base.BaseWidget, object):

    renameUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(RenamerView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(RenamerView, self).ui()

        renamer_widget = QWidget()
        renamer_widget.setLayout(layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0)))
        renamer_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.main_layout.addWidget(renamer_widget)

        rename_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        rename_layout.setAlignment(Qt.AlignLeft)
        renamer_widget.layout().addLayout(rename_layout)

        self._base_name_cbx = checkbox.BaseCheckBox(parent=self)
        rename_layout.addWidget(self._base_name_cbx)
        self._renamer_line = lineedit.BaseLineEdit(parent=self)
        self._renamer_line.setPlaceholderText('New Name')

        rename_layout.addWidget(self._renamer_line)
        reg_ex = QRegExp("^(?!^_)[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._renamer_line)
        self._renamer_line.setValidator(text_validator)
        self._renamer_btn = buttons.BaseButton(parent=self)
        self._renamer_btn.setIcon(tp.ResourcesMgr().icon('rename'))
        rename_layout.addWidget(self._renamer_btn)

    def setup_signals(self):
        self._base_name_cbx.toggled.connect(self._controller.toggle_check)
        self._renamer_line.textChanged.connect(self._controller.change_name)
        self._renamer_btn.clicked.connect(self._controller.rename_simple)

        self._model.checkChanged.connect(self._on_check_toggled)
        self._model.nameChanged.connect(self._on_name_changed)

    def refresh(self):
        """
        Syncs view to the current state of its model
        """

        self._base_name_cbx.setChecked(self._model.check)
        self._renamer_line.setText(self._model.name)

    def _on_check_toggled(self, flag):
        self._base_name_cbx.setChecked(flag)
        self._renamer_line.setEnabled(flag)
        self._renamer_btn.setEnabled(flag)
        # self.renameUpdate.emit()

    def _on_name_changed(self, new_name):
        self._renamer_line.setText(new_name)
        # self.renameUpdate.emit()


class RenamerWidgetModel(QObject, object):

    checkChanged = Signal(bool)
    nameChanged = Signal(str)
    doRename = Signal()

    def __init__(self):
        super(RenamerWidgetModel, self).__init__()

        self._global_data = dict()
        self._check = True
        self._name = ''

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict

    @property
    def check(self):
        return self._check

    @check.setter
    def check(self, flag):
        self._check = bool(flag)
        self.checkChanged.emit(self._check)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)
        self.nameChanged.emit(self._name)

    @property
    def rename_settings(self):
        text = str(self.name.strip()) if self.check else ''

        return {
            'name': text
        }


class RenamerWidgetController(object):
    def __init__(self, client, model):
        super(RenamerWidgetController, self).__init__()

        self._client = client
        self._model = model

    def toggle_check(self, flag):
        self._model.check = flag

    def change_name(self, new_name):
        self._model.name = new_name

    @tp.Dcc.get_undo_decorator()
    def rename_simple(self):
        global_data = self._model.global_data
        new_name = self._model.name
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        selection_type = global_data.get('selection_type', 0)
        nodes = utils.get_objects_to_rename(hierarchy_check=hierarchy_check, selection_type=selection_type)

        return self._client.simple_rename(new_name, rename_shape=rename_shape, nodes=nodes)


def renamer_widget(client, parent=None):

    model = RenamerWidgetModel()
    controller = RenamerWidgetController(client=client, model=model)
    view = RenamerView(model=model, controller=controller, parent=parent)

    return view
