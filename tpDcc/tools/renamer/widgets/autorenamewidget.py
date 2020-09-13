#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains auto rename widgets for tpRenamer
"""

from __future__ import print_function, division, absolute_import

import traceback
from functools import partial
from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base, qtutils
from tpDcc.libs.qt.widgets import layouts, buttons, dividers, combobox, label, lineedit, checkbox

LOGGER = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


class AutoRenameWidget(base.BaseWidget, object):
    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller
        self._token_widgets = OrderedDict()

        super(AutoRenameWidget, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(AutoRenameWidget, self).ui()

        top_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        self._unique_id_cbx = checkbox.BaseCheckBox('Unique Id')
        self._last_joint_end_cbx = checkbox.BaseCheckBox('Make Last Joint End')
        top_layout.addStretch()
        top_layout.addWidget(self._unique_id_cbx)
        top_layout.addWidget(self._last_joint_end_cbx)
        self.main_layout.addLayout(top_layout)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        auto_widget = QWidget()
        auto_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        auto_widget.setLayout(auto_layout)
        main_splitter.addWidget(auto_widget)

        self._rules_list = QTreeWidget(self)
        self._rules_list.setHeaderHidden(True)
        self._rules_list.setSortingEnabled(True)
        self._rules_list.setRootIsDecorated(False)
        self._rules_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._rules_list.sortByColumn(0, Qt.AscendingOrder)
        self._rules_list.setUniformRowHeights(True)
        self._rules_list.setAlternatingRowColors(True)

        auto_layout.addWidget(self._rules_list)

        auto_w = QWidget()
        self.auto_l = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        auto_w.setLayout(self.auto_l)
        auto_w.setMinimumWidth(200)
        main_splitter.addWidget(auto_w)

        self.main_auto_layout = QFormLayout()
        self.auto_l.addLayout(self.main_auto_layout)

        self._rename_btn = buttons.BaseButton('Rename')
        self._rename_btn.setIcon(tp.ResourcesMgr().icon('rename'))
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._rename_btn)

    def setup_signals(self):
        self._unique_id_cbx.toggled.connect(self._controller.change_unique_id_auto)
        self._last_joint_end_cbx.toggled.connect(self._controller.change_last_joint_end_auto)
        self._rules_list.currentItemChanged.connect(self._controller.change_selected_rule)
        self._model.globalAttributeChanged.connect(self._on_updated_global_attribute)
        self._rename_btn.clicked.connect(self._on_rename)

        self._model.rulesChanged.connect(self._on_update_rules)
        self._model.activeRuleChanged.connect(self._on_update_active_rule)
        self._model.uniqueIdAutoChanged.connect(self._unique_id_cbx.setChecked)
        self._model.lastJointEndAutoChanged.connect(self._last_joint_end_cbx.setChecked)

    def refresh(self):
        self._unique_id_cbx.setChecked(self._model.unique_id_auto)
        self._last_joint_end_cbx.setChecked(self._model.last_joint_end_auto)

    def _add_token(self, token_name, line_layout):
        self.main_auto_layout.addRow(token_name, line_layout)

    def _on_update_rules(self, new_rules):

        active_rule = self._model.active_rule
        item_to_select = None

        self._rules_list.clear()

        self._rules_list.blockSignals(True)
        try:
            for rule in new_rules:
                item = QTreeWidgetItem(self._rules_list, [rule.name])
                item.rule = rule
                self._rules_list.addTopLevelItem(item)
                self._rules_list.setCurrentItem(item)
                if active_rule and active_rule == rule.name:
                    item_to_select = item
                self._rules_list.setItemSelected(item, False)

            if item_to_select:
                self._rules_list.setItemSelected(item_to_select, True)
        except Exception as exc:
            LOGGER.error('{} | {}'.format(exc, traceback.format_exc()))
        finally:
            self._rules_list.blockSignals(False)

        self._on_update_active_rule(active_rule=self._model.active_rule)

    def _on_update_active_rule(self, active_rule):
        if not active_rule:
            return

        qtutils.clear_layout(self.main_auto_layout)

        if not active_rule:
            return

        tokens = self._model.tokens

        active_tokens = list()
        for field in active_rule.fields():
            for token in tokens:
                if token.name == field:
                    active_tokens.append(token)

        self._token_widgets.clear()

        for token in reversed(active_tokens):
            token_name = token.name
            token_value = token.get_items()
            token_default = token.default

            if token_name == 'id':
                continue

            if token_value:
                w = combobox.BaseComboBox(parent=self)
                w_l = label.BaseLabel(parent=self)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                w_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._add_token(token_name, qtutils.get_line_layout('', self, w, QLabel(u'\u25ba'), w_l))
                for key, value in token_value.items():
                    if key == 'default':
                        continue
                    w.addItem(key)
                try:
                    if token_default > 0:
                        w.setCurrentIndex(token_default - 1)
                except Exception:
                    w.setCurrentIndex(0)
                current_text = w.currentText()
                try:
                    current_value = token.solve(self._naming_lib.active_rule(), current_text)
                    w_l.setText(str(current_value))
                except Exception:
                    pass
                w.currentTextChanged.connect(partial(self._on_combo_changed, token))
                self._token_widgets[token_name] = {'widget': [w, w_l], 'fn': w.currentText}
            else:
                w = lineedit.BaseLineEdit(parent=self)
                # w.textChanged.connect(self._on_text_changed)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = {'widget': [w], 'fn': w.text}
                self._add_token(token_name, qtutils.get_line_layout('', self, w))

    def _on_combo_changed(self, token, text):
        active_rule = self._model.active_rule
        if not active_rule:
            return

        token_name = token.name
        if token_name not in self._token_widgets:
            return
        token_widgets = self._token_widgets[token_name]['widget']
        try:
            current_value = token.solve(active_rule, text)
            token_widgets[1].setText(str(current_value))
        except Exception:
            pass
        # self.renameUpdated.emit()

#     def _on_text_changed(self, text):
#         self.renameUpdated.emit()

    def _on_updated_global_attribute(self):

        self._global_attributes_dict = {
            'selection_type': self._model.selection_type,
            'filter_type': self._model.filter_type,
            'hierarchy_check': self._model.hierarchy_check,
            'rename_shape': self._model.rename_shape,
            'only_selection': True if self._model.selection_type == 0 else False
        }

    def _on_rename(self):

        tokens_dict = dict()
        for token_name, token_data in self._token_widgets.items():
            token_value_fn = token_data['fn']
            token_value = token_value_fn()
            tokens_dict[token_name] = token_value

        unique_id = self._model.unique_id_auto
        last_joint_end = self._model.last_joint_end_auto

        return self._controller.auto_rename(tokens_dict, unique_id=unique_id, last_joint_end=last_joint_end)
