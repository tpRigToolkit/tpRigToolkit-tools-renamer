#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages prefix/suffix rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import splitters


class PrefixSuffixWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    doAddPrefix = Signal(str)
    doRemovePrefix = Signal()
    doAddSuffix = Signal(str)
    doRemoveSuffix = Signal()
    doRemoveFirst = Signal(int)
    doRemoveLast = Signal(int)
    
    def __init__(self, parent=None):

        self._config = tpDcc.ToolsMgr().get_tool_config('tpDcc-tools-renamer')

        super(PrefixSuffixWidget, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(PrefixSuffixWidget, self).ui()

        prefix_layout = QHBoxLayout()
        prefix_layout.setAlignment(Qt.AlignLeft)
        prefix_layout.setContentsMargins(0, 0, 0, 0)
        prefix_layout.setSpacing(5)
        self.main_layout.addLayout(prefix_layout)
        self._prefix_cbx = QCheckBox()
        self._prefix_cbx.setChecked(True)
        prefix_layout.addWidget(self._prefix_cbx)
        prefix_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._prefix_line = QLineEdit()
        self._prefix_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._prefix_line.setPlaceholderText('Prefix')
        prefix_reg_exp = QRegExp("^(?!^_)[a-zA-Z_]+")
        prefix_validator = QRegExpValidator(prefix_reg_exp, self._prefix_line)
        self._prefix_line.setValidator(prefix_validator)
        self._prefix_combo = QComboBox()
        self._prefix_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        prefix_layout.addWidget(self._prefix_line)
        prefix_layout.addWidget(self._prefix_combo)
        self._prefix_btn = QPushButton()
        self._prefix_btn.setIcon(tpDcc.ResourcesMgr().icon('prefix'))
        self._remove_prefix_btn = QPushButton()
        self._remove_prefix_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        prefix_layout.addWidget(self._prefix_btn)
        prefix_layout.addWidget(self._remove_prefix_btn)

        remove_first_layout = QHBoxLayout()
        remove_first_layout.setAlignment(Qt.AlignLeft)
        remove_first_layout.setContentsMargins(0, 0, 0, 0)
        remove_first_layout.setSpacing(2)
        self.main_layout.addLayout(remove_first_layout)
        self._remove_first_cbx = QCheckBox()
        remove_first_layout.addWidget(self._remove_first_cbx)
        remove_first_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._remove_first_lbl = QLabel('Remove first: ')
        self._remove_first_spn = QSpinBox()
        self._remove_first_spn.setFocusPolicy(Qt.NoFocus)
        self._remove_first_spn.setMinimum(0)
        self._remove_first_spn.setMaximum(99)
        last_digits_lbl = QLabel(' digits')
        remove_first_layout.addWidget(self._remove_first_lbl)
        remove_first_layout.addWidget(self._remove_first_spn)
        remove_first_layout.addWidget(last_digits_lbl)
        self._remove_first_lbl.setEnabled(False)
        self._remove_first_spn.setEnabled(False)
        self._remove_first_btn = QPushButton()
        self._remove_first_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        self._remove_first_btn.setEnabled(False)
        remove_first_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        remove_first_layout.addWidget(self._remove_first_btn)

        self.main_layout.addLayout(splitters.SplitterLayout())

        suffix_layout = QHBoxLayout()
        suffix_layout.setAlignment(Qt.AlignLeft)
        suffix_layout.setContentsMargins(0, 0, 0, 0)
        suffix_layout.setSpacing(5)
        self.main_layout.addLayout(suffix_layout)
        self._suffix_cbx = QCheckBox()
        self._suffix_cbx.setChecked(True)
        suffix_layout.addWidget(self._suffix_cbx)
        suffix_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._suffix_line = QLineEdit()
        self._suffix_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        suffix_reg_exp = QRegExp("^[a-zA-Z_0-9]+")
        suffix_validator = QRegExpValidator(suffix_reg_exp, self._suffix_line)
        self._suffix_line.setValidator(suffix_validator)
        self._suffix_line.setPlaceholderText('Suffix')
        self._suffix_combo = QComboBox()
        self._suffix_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        suffix_layout.addWidget(self._suffix_line)
        suffix_layout.addWidget(self._suffix_combo)
        self._suffix_btn = QPushButton()
        self._suffix_btn.setIcon(tpDcc.ResourcesMgr().icon('suffix'))
        self._remove_suffix_btn = QPushButton()
        self._remove_suffix_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        suffix_layout.addWidget(self._suffix_btn)
        suffix_layout.addWidget(self._remove_suffix_btn)

        remove_last_layout = QHBoxLayout()
        remove_last_layout.setAlignment(Qt.AlignLeft)
        remove_last_layout.setContentsMargins(0, 0, 0, 0)
        remove_last_layout.setSpacing(5)
        self.main_layout.addLayout(remove_last_layout)
        self._remove_last_cbx = QCheckBox()
        remove_last_layout.addWidget(self._remove_last_cbx)
        remove_last_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._remove_last_lbl = QLabel('Remove last: ')
        self._remove_last_spn = QSpinBox()
        self._remove_last_spn.setEnabled(False)
        self._remove_last_spn.setMinimum(0)
        self._remove_last_spn.setMaximum(99)
        last_digits_lbl2 = QLabel(' digits')
        remove_last_layout.addWidget(self._remove_last_lbl)
        remove_last_layout.addWidget(self._remove_last_spn)
        remove_last_layout.addWidget(last_digits_lbl2)
        self._remove_last_lbl.setEnabled(False)
        self._remove_last_spn.setEnabled(False)
        self._remove_last_btn = QPushButton()
        self._remove_last_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        self._remove_last_btn.setEnabled(False)
        remove_last_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        remove_last_layout.addWidget(self._remove_last_btn)

        last_joint_layout = QHBoxLayout()
        last_joint_layout.setAlignment(Qt.AlignLeft)
        last_joint_layout.setContentsMargins(0, 0, 0, 0)
        last_joint_layout.setSpacing(2)
        self.main_layout.addLayout(last_joint_layout)
        self._last_joint_is_end_cbx = QCheckBox()
        self._last_joint_is_end_lbl = QLabel('Last joint is an endJoint?')
        self._last_joint_is_end_cbx.setChecked(True)
        last_joint_layout.addWidget(self._last_joint_is_end_cbx)
        last_joint_layout.addWidget(splitters.get_horizontal_separator_widget())
        last_joint_layout.addWidget(self._last_joint_is_end_lbl)

    def setup_signals(self):
        self._prefix_cbx.toggled.connect(self._on_prefix_toggled)
        self._prefix_line.textChanged.connect(self._on_prefx_line_text_changed)
        self._remove_first_cbx.toggled.connect(self._on_remove_first_toggled)
        self._remove_first_spn.valueChanged.connect(self._on_remove_first_value_changed)
        self._suffix_cbx.toggled.connect(self._on_suffix_toggled)
        self._suffix_line.textChanged.connect(self._on_suffix_line_text_changed)
        self._remove_last_cbx.toggled.connect(self._on_remove_last_toggled)
        self._remove_last_spn.valueChanged.connect(self._on_remove_last_value_changed)
        self._prefix_combo.currentIndexChanged.connect(self._on_prefix_selected)
        self._suffix_combo.currentIndexChanged.connect(self._on_suffix_selected)
        self._prefix_btn.clicked.connect(self._on_add_prefix)
        self._remove_prefix_btn.clicked.connect(self._on_remove_prefix)
        self._suffix_btn.clicked.connect(self._on_add_suffix)
        self._remove_suffix_btn.clicked.connect(self._on_remove_suffix)
        self._remove_first_btn.clicked.connect(self._on_remove_first)
        self._remove_last_btn.clicked.connect(self._on_remove_last)

    def refresh(self):
        """
        :return:
        """

        self._prefix_combo.clear()
        self._suffix_combo.clear()

        if not self._config:
            return

        suffixes = self._config.get('suffixes', default=list())
        if not suffixes:
            naming_config = tpDcc.ConfigsMgr().get_config('tpDcc-naming')
            if naming_config:
                suffixes = naming_config.get('suffixes', default=dict())

        self._prefix_combo.setVisible(bool(suffixes))
        self._suffix_combo.setVisible(bool(suffixes))
        if not suffixes:
            return

        self._prefix_combo.addItem('Select prefix ...')
        self._suffix_combo.addItem('Select suffix ...')
        format_items = ['{}: "{}"'.format(suffix.keys()[0], suffix.values()[0]) for suffix in suffixes]
        for i, item in enumerate(format_items):
            item_index = i + 1      # First index if selected prefix/suffix items ...
            self._prefix_combo.addItem(item)
            self._suffix_combo.addItem(item)
            self._prefix_combo.setItemData(item_index, suffixes[i].values()[0])
            self._suffix_combo.setItemData(item_index, suffixes[i].values()[0])

        self.renameUpdate.emit()

    def get_rename_settings(self):
        """
        :return:
        """

        prefix = ''
        suffix = ''

        if self._prefix_cbx.isChecked():
            prefix = self._prefix_line.text()
        if self._suffix_cbx.isChecked():
            suffix = self._suffix_line.text()

        if not self._remove_first_cbx.isChecked():
            remove_first = 0
        else:
            remove_first = self._remove_first_spn.value()

        if not self._remove_last_cbx.isChecked():
            remove_last = 0
        else:
            remove_last = self._remove_last_spn.value()

        joint_end = self._last_joint_is_end_cbx.isChecked()

        return prefix, suffix, remove_first, remove_last, joint_end

    def _on_prefix_toggled(self, flag):
        self._prefix_line.setEnabled(flag)
        self._prefix_combo.setEnabled(flag)
        self._prefix_btn.setEnabled(flag)
        self._remove_prefix_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_remove_first_toggled(self, flag):
        self._remove_first_lbl.setEnabled(flag)
        self._remove_first_spn.setEnabled(flag)
        self._remove_first_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_suffix_toggled(self, flag):
        self._suffix_line.setEnabled(flag)
        self._suffix_combo.setEnabled(flag)
        self._suffix_btn.setEnabled(flag)
        self._remove_suffix_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_remove_last_toggled(self, flag):
        self._remove_last_lbl.setEnabled(flag)
        self._remove_last_spn.setEnabled(flag)
        self._remove_last_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_prefx_line_text_changed(self):
        self.renameUpdate.emit()

    def _on_suffix_line_text_changed(self):
        self.renameUpdate.emit()

    def _on_remove_first_value_changed(self):
        self.renameUpdate.emit()

    def _on_remove_last_value_changed(self):
        self.renameUpdate.emit()

    def _on_prefix_selected(self, index):
        if index == 0:
            return

        prefix_selected = self._prefix_combo.itemData(index)
        self._prefix_line.setText('{}_'.format(prefix_selected))

    def _on_suffix_selected(self, index):
        if index == 0:
            return

        suffix_selected = self._suffix_combo.itemData(index)
        self._suffix_line.setText('{}_'.format(suffix_selected))

    def _on_add_prefix(self):
        """
        Internal callback function that is called when add prefix button is clicked
        """

        self.doAddPrefix.emit(self._prefix_line.text())

    def _on_add_suffix(self):
        """
        Internal callback function that is called when add prefix button is clicked
        """

        self.doAddSuffix.emit(self._suffix_line.text())

    def _on_remove_prefix(self):
        """
        Internal callback function that is called when remove prefix button is clicked
        """

        self.doRemovePrefix.emit()

    def _on_remove_suffix(self):
        """
        Internal callback function that is called when remove prefix button is clicked
        """

        self.doRemoveSuffix.emit()

    def _on_remove_first(self):
        """
        Internal callback function that is called when remove first characters button is clicked
        """

        self.doRemoveFirst.emit(self._remove_first_spn.value())
    
    def _on_remove_last(self):
        """
        Internal callback function that is called when remove last characters button is clicked
        """

        self.doRemoveLast.emit(self._remove_last_spn.value())
