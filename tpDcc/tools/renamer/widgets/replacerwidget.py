#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages replace functionality for tpRenamer
"""

from __future__ import print_function, division, absolute_import


from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, checkbox, lineedit, buttons

from tpDcc.tools.renamer.core import utils


class ReplacerView(base.BaseWidget, object):
    # replaceUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(ReplacerView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(ReplacerView, self).ui()

        replace_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        replace_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(replace_layout)

        self._find_replace_cbx = checkbox.BaseCheckBox(parent=self)
        replace_layout.addWidget(self._find_replace_cbx)

        self._replace_line = lineedit.BaseLineEdit(parent=self)
        self._replace_line.setPlaceholderText('Search')
        self._with_line = lineedit.BaseLineEdit(parent=self)
        self._with_line.setPlaceholderText('Replace')
        reg_ex = QRegExp("[a-zA-Z_0-9]+")
        text_validator = QRegExpValidator(reg_ex, self._replace_line)
        self._replace_line.setValidator(text_validator)
        self._with_line.setValidator(text_validator)
        self._search_replace_btn = buttons.BaseButton(parent=self)
        self._search_replace_btn.setIcon(tp.ResourcesMgr().icon('find_replace'))

        replace_layout.addWidget(self._replace_line)
        replace_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        replace_layout.addWidget(self._with_line)
        replace_layout.addWidget(self._search_replace_btn)

        self._replace_line.setEnabled(False)
        self._with_line.setEnabled(False)

    def setup_signals(self):
        self._find_replace_cbx.toggled.connect(self._controller.toggle_search_replace_check)
        self._replace_line.textChanged.connect(self._controller.change_search)
        self._with_line.textChanged.connect(self._controller.change_replace)
        self._search_replace_btn.clicked.connect(self._controller.search_and_replace)

        self._model.searchReplaceCheckChanged.connect(self._on_find_replace_toggled)
        self._model.searchChanged.connect(self._on_search_changed)
        self._model.replaceChanged.connect(self._on_replace_changed)

    def refresh(self):
        self._find_replace_cbx.setChecked(self._model.search_replace_check)
        self._replace_line.setText(self._model.search)
        self._with_line.setText(self._model.replace)

    def _on_find_replace_toggled(self, flag):
        self._find_replace_cbx.setChecked(flag)
        self._replace_line.setEnabled(flag)
        self._with_line.setEnabled(flag)
        self._search_replace_btn.setEnabled(flag)
        # self.replaceUpdate.emit()

    def _on_search_changed(self, new_text):
        self._replace_line.setText(new_text)
        # self.replaceUpdate.emit()

    def _on_replace_changed(self, new_text):
        self._with_line.setText(new_text)
        # self.replaceUpdate.emit()


class ReplacerWidgetModel(QObject, object):

    searchReplaceCheckChanged = Signal(bool)
    searchChanged = Signal(str)
    replaceChanged = Signal(str)

    def __init__(self):
        super(ReplacerWidgetModel, self).__init__()

        self._global_data = dict()
        self._search_replace_check = False
        self._search = ''
        self._replace = ''

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict

    @property
    def search_replace_check(self):
        return self._search_replace_check

    @search_replace_check.setter
    def search_replace_check(self, value):
        self._search_replace_check = bool(value)
        self.searchReplaceCheckChanged.emit(self._search_replace_check)

    @property
    def search(self):
        return self._search

    @search.setter
    def search(self, value):
        self._search = str(value)
        self.searchChanged.emit(self._search)

    @property
    def replace(self):
        return self._replace

    @replace.setter
    def replace(self, value):
        self._replace = str(value)
        self.replaceChanged.emit(self._replace)

    @property
    def rename_settings(self):
        search_str = self.search if self.search_replace_check else ''
        replace_str = self.replace if self.search_replace_check else ''

        return {
            'search': search_str,
            'replace': replace_str
        }


class ReplacerWidgetController(object):
    def __init__(self, client, model):
        super(ReplacerWidgetController, self).__init__()

        self._client = client
        self._model = model

    def toggle_search_replace_check(self, flag):
        self._model.search_replace_check = flag

    def change_search(self, value):
        self._model.search = value

    def change_replace(self, value):
        self._model.replace = value

    @tp.Dcc.get_undo_decorator()
    def search_and_replace(self):
        global_data = self._model.global_data
        search_str = self._model.search
        replace_str = self._model.replace
        hierarchy_check = global_data.get('hierarchy_check', False)
        selection_type = global_data.get('selection_type', 0)
        nodes = utils.get_objects_to_rename(hierarchy_check=hierarchy_check, selection_type=selection_type)

        return self._client.search_and_replace(search_str, replace_str, nodes=nodes)


def replacer_widget(client, parent=None):

    model = ReplacerWidgetModel()
    controller = ReplacerWidgetController(client=client, model=model)
    view = ReplacerView(model=model, controller=controller, parent=parent)

    return view
