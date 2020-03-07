#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages basic rename functionality for tpRenamer
"""

from __future__ import print_function, division, absolute_import


from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import splitters


class RenamerWidget(base.BaseWidget, object):
    
    doName = Signal(str)
    renameUpdate = Signal()

    def __init__(self, parent=None):
        super(RenamerWidget, self).__init__(parent=parent)

        self._base_name_cbx.setChecked(True)

    def ui(self):
        super(RenamerWidget, self).ui()

        renamer_widget = QWidget()
        renamer_widget.setLayout(QVBoxLayout())
        renamer_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        renamer_widget.layout().setContentsMargins(0, 0, 0, 0)
        renamer_widget.layout().setSpacing(2)
        self.main_layout.addWidget(renamer_widget)

        rename_layout = QHBoxLayout()
        rename_layout.setAlignment(Qt.AlignLeft)
        rename_layout.setContentsMargins(0, 0, 0, 0)
        rename_layout.setSpacing(2)
        renamer_widget.layout().addLayout(rename_layout)
        self._base_name_cbx = QCheckBox()
        rename_layout.addWidget(self._base_name_cbx)
        rename_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._renamer_line = QLineEdit()
        self._renamer_line.setPlaceholderText('New Name')

        rename_layout.addWidget(self._renamer_line)
        reg_ex = QRegExp("^(?!^_)[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._renamer_line)
        self._renamer_line.setValidator(text_validator)
        self._renamer_line.setEnabled(False)
        self._renamer_btn = QPushButton()
        self._renamer_btn.setIcon(tpDcc.ResourcesMgr().icon('rename'))
        self._renamer_btn.setEnabled(False)
        rename_layout.addWidget(self._renamer_btn)

    def setup_signals(self):
        self._base_name_cbx.toggled.connect(self._on_base_name_toggled)
        self._renamer_line.textChanged.connect(self._on_rename_line_text_changed)
        self._renamer_btn.clicked.connect(self._on_rename)

    def get_rename_settings(self):
        """
        Internal function that returns current rename settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        if self._base_name_cbx.isChecked():
            text = str(self._renamer_line.text()).strip()
        else:
            text = ''

        return text

    def _on_base_name_toggled(self, flag):
        self._renamer_line.setEnabled(flag)
        self._renamer_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_rename_line_text_changed(self, new_text):
        self.renameUpdate.emit()

    def _on_rename(self):
        """
        Internal callback function that renames current selected nodes
        """

        new_name = self._renamer_line.text()
        if not new_name:
            return
        self.doName.emit(new_name)
