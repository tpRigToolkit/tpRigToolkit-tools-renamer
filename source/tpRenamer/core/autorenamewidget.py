#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains auto rename widgets for tpRenamer
"""

from __future__ import print_function, division, absolute_import

import traceback
from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base, qtutils
from tpQtLib.widgets import button

import tpRenamer

NAMING_IT_AVAILABLE = True
try:
    import tpNameIt
    from tpNameIt.core import nameit
except ImportError:
    NAMING_IT_AVAILABLE = False


class AutoRenameWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(AutoRenameWidget, self).__init__(parent=parent)

        self._token_widgets = dict()

    def ui(self):
        super(AutoRenameWidget, self).ui()

        main_splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(main_splitter)

        auto_widget = QWidget()
        auto_layout = QVBoxLayout()
        auto_widget.setLayout(auto_layout)
        main_splitter.addWidget(auto_widget)

        edit_icon = tpRenamer.resource.icon('edit', extension='png')
        self.edit_btn = button.IconButton(icon=edit_icon, icon_padding=2, button_style=button.ButtonStyles.FlatStyle)
        self.rules_list = QTreeWidget(self)
        self.rules_list.setHeaderHidden(True)
        self.rules_list.setSortingEnabled(True)
        self.rules_list.setRootIsDecorated(False)
        self.rules_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rules_list.sortByColumn(0, Qt.AscendingOrder)
        self.rules_list.setUniformRowHeights(True)
        self.rules_list.setAlternatingRowColors(True)
        self.rules_list.setStyleSheet(
            '''
            QTreeView{alternate-background-color: #3b3b3b;}
            QTreeView::item {padding:3px;}
            QTreeView::item:!selected:hover {
                background-color: #5b5b5b;
                margin-left:-3px;
                border-left:0px;
            }
            QTreeView::item:selected {
                background-color: #48546a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            QTreeView::item:selected:hover {
                background-color: #586c7a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            '''
        )

        auto_layout.addWidget(self.edit_btn)
        auto_layout.addWidget(self.rules_list)

        auto_w = QWidget()
        self.auto_l = QVBoxLayout()
        # self.auto_l.setAlignment(Qt.AlignTop)
        auto_w.setLayout(self.auto_l)
        auto_w.setMinimumWidth(200)
        main_splitter.addWidget(auto_w)

        self.main_auto_layout = QFormLayout()
        self.auto_l.addLayout(self.main_auto_layout)

    def setup_signals(self):
        self.edit_btn.clicked.connect(self._on_open_naming_manager)

    def add_token(self, token_name, line_layout):
        self.main_auto_layout.addRow(token_name, line_layout)

    def update_rules(self):
        if not NAMING_IT_AVAILABLE:
            return

        self.rules_list.blockSignals(True)

        try:
            self.rules_list.clear()
            item_to_select = None
            current_rule = nameit.NameIt.get_active_rule()
            qtutils.clear_layout(self.auto_l)
            rules = nameit.NamingData.get_rules()
            for rule in rules:
                item = QTreeWidgetItem(self.rules_list, [rule.name])
                item.rule = rule
                self.rules_list.addTopLevelItem(item)
                self.rules_list.setCurrentItem(item)
                if current_rule and current_rule.name() == rule.name:
                    item_to_select = item
                self.rules_list.setItemSelected(item, False)
            if item_to_select:
                self.rules_list.setItemSelected(item_to_select, True)
        except Exception as e:
            tpRenamer.logger.error('{} | {}'.format(e, traceback.format_exc()))
        finally:
            self.rules_list.blockSignals(False)

        self._on_change_name_rule()

    def _on_change_name_rule(self):

        qtutils.clear_layout(self.main_auto_layout)

        rule_item = self.rules_list.currentItem()
        if not rule_item:
            return

        current_rule = nameit.NameIt.get_active_rule()
        nameit.NameIt.set_active_rule(name=rule_item.rule.name)
        rule_tokens = nameit.NamingData.get_tokens()

        active_tokens = list()
        active_rule = nameit.NameIt.get_active_rule()
        for field in active_rule.fields():
            for token in rule_tokens:
                if token.name == field:
                    active_tokens.append(token)

        self._token_widgets = OrderedDict()

        for token in reversed(active_tokens):
            token_name = token.name
            token_value = token.get_values_as_keyword()
            token_default = token.default

            if token_name == 'id':
                continue

            if token_value:
                w = QComboBox()
                w_l = QLabel()
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                w_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = [w, w_l]
                self.add_token(token_name, qtutils.get_line_layout('', self, w, QLabel(u'\u25ba'), w_l))
                for key, value in token_value.items():
                    if key == 'default':
                        continue
                    w.addItem(key)
                if token_default > 0:
                    w.setCurrentIndex(token_default-1)
            else:
                w = QLineEdit(self)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = w
                self.add_token(token_name, qtutils.get_line_layout('', self, w))

        if current_rule:
            nameit.NameIt.set_active_rule(current_rule.name)

    def _on_open_naming_manager(self):
        if not NAMING_IT_AVAILABLE:
            return

        win = nameit.run()

        return win