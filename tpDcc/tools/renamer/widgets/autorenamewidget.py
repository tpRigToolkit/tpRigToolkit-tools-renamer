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

import tpDcc
from tpDcc.libs.qt.core import base, qtutils
from tpDcc.libs.qt.widgets import dividers


class AutoRenameWidget(base.BaseWidget, object):

    doRename = Signal(str, dict)
    renameUpdated = Signal()

    def __init__(self, naming_lib, parent=None):
        self._naming_lib = naming_lib
        super(AutoRenameWidget, self).__init__(parent=parent)

        self._token_widgets = dict()

    def setup_signals(self):
        self._rules_list.itemSelectionChanged.connect(self._on_item_selection_changed)
        self._rename_btn.clicked.connect(self._on_do_rename)

    def get_rename_settings(self):
        rename_settings = dict()

        if not self._token_widgets:
            return rename_settings

        for token_name, widget in self._token_widgets.items():
            if isinstance(widget, list):
                rename_settings[token_name] = widget[0].currentText()
            elif isinstance(widget, QLineEdit):
                rename_settings[token_name] = widget.text()

        return rename_settings

    def add_token(self, token_name, line_layout):
        self.main_auto_layout.addRow(token_name, line_layout)

    def update_rules(self):
        self._rules_list.blockSignals(True)

        try:
            self._rules_list.clear()
            item_to_select = None
            current_rule = self._naming_lib.active_rule()
            qtutils.clear_layout(self.main_auto_layout)
            rules = self._naming_lib.rules
            for rule in rules:
                item = QTreeWidgetItem(self._rules_list, [rule.name])
                item.rule = rule
                self._rules_list.addTopLevelItem(item)
                self._rules_list.setCurrentItem(item)
                if current_rule and current_rule == rule.name:
                    item_to_select = item
                self._rules_list.setItemSelected(item, False)
            if item_to_select:
                self._rules_list.setItemSelected(item_to_select, True)
        except Exception as e:
            tpDcc.logger.error('{} | {}'.format(e, traceback.format_exc()))
        finally:
            self._rules_list.blockSignals(False)

        self._on_change_name_rule()

    def _on_change_name_rule(self):

        qtutils.clear_layout(self.main_auto_layout)

        rule_item = self._rules_list.currentItem()
        if not rule_item:
            return

        current_rule = self._naming_lib.active_rule()
        self._naming_lib.set_active_rule(name=rule_item.rule.name)
        rule_tokens = self._naming_lib.tokens

        active_tokens = list()
        active_rule = self._naming_lib.active_rule()
        for field in active_rule.fields():
            for token in rule_tokens:
                if token.name == field:
                    active_tokens.append(token)

        self._token_widgets = OrderedDict()

        for token in reversed(active_tokens):
            token_name = token.name
            token_value = token.get_items()
            token_default = token.default

            if token_name == 'id':
                continue

            if token_value:
                w = QComboBox()
                w_l = QLabel()
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                w_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.add_token(token_name, qtutils.get_line_layout('', self, w, QLabel(u'\u25ba'), w_l))
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
                w = QLineEdit(self)
                w.textChanged.connect(self._on_text_changed)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = {'widget': [w], 'fn': w.text}
                self.add_token(token_name, qtutils.get_line_layout('', self, w))

        if current_rule:
            self._naming_lib.set_active_rule(current_rule.name)

    def _on_combo_changed(self, token, text):
        token_name = token.name
        if token_name not in self._token_widgets:
            return
        token_widgets = self._token_widgets[token_name]['widget']
        try:
            current_value = token.solve(self._naming_lib.active_rule(), text)
            token_widgets[1].setText(str(current_value))
        except Exception:
            pass
        self.renameUpdated.emit()

    def _on_text_changed(self, text):
        self.renameUpdated.emit()

    def _on_item_selection_changed(self):
        current_item = self._rules_list.currentItem()
        current_rule = current_item.rule
        self._naming_lib.set_active_rule(current_rule.name)
        self._on_change_name_rule()

    def _on_do_rename(self):
        rule_item = self._rules_list.currentItem()
        if not rule_item:
            return

        self.doRename.emit(rule_item.rule.name, self._token_widgets)
