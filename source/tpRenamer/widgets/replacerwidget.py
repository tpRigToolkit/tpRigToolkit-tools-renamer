#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages replace functionality for tpRenamer
"""

from __future__ import print_function, division, absolute_import


from tpQtLib.Qt.QtCore import *
from tpQtLib.Qt.QtWidgets import *
from tpQtLib.Qt.QtGui import *

from tpQtLib.core import base
from tpQtLib.widgets import splitters, expandables


class ReplacerWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(ReplacerWidget, self).__init__(parent=parent)

    def ui(self):
        super(ReplacerWidget, self).ui()

        self.main_layout.addWidget(splitters.Splitter('REPLACE'))

        replace_layout = QHBoxLayout()
        replace_layout.setAlignment(Qt.AlignLeft)
        replace_layout.setContentsMargins(0, 0, 0, 0)
        replace_layout.setSpacing(2)
        self.main_layout.addLayout(replace_layout)

        self._find_replace_cbx = QCheckBox()
        replace_layout.addWidget(self._find_replace_cbx)
        replace_layout.addWidget(splitters.get_horizontal_separator_widget())

        replace_lbl = QLabel('Find: ')
        self._replace_line = QLineEdit()
        with_lbl = QLabel('Replace: ')
        self._with_line = QLineEdit()
        # replace_lbl.setFixedWidth(55)
        # with_lbl.setFixedWidth(55)
        reg_ex = QRegExp("[a-zA-Z_0-9]+")
        text_validator = QRegExpValidator(reg_ex, self._replace_line)
        self._replace_line.setValidator(text_validator)
        self._with_line.setValidator(text_validator)

        replace_layout.addWidget(replace_lbl)
        replace_layout.addWidget(self._replace_line)
        replace_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        replace_layout.addWidget(with_lbl)
        replace_layout.addWidget(self._with_line)
