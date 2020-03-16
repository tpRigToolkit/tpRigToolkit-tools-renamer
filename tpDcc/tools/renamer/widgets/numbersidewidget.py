#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages index rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import splitters


class NumberSideWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    doReplacePadding = Signal(int)
    doAppendPadding = Signal(int)
    doChangePadding = Signal(int)
    doSide = Signal(str)

    def __init__(self, parent=None):
        super(NumberSideWidget, self).__init__(parent=parent)

    def ui(self):
        super(NumberSideWidget, self).ui()

        rename_mult_layout = QHBoxLayout()
        rename_mult_layout.setAlignment(Qt.AlignLeft)
        rename_mult_layout.setContentsMargins(0, 0, 0, 0)
        rename_mult_layout.setSpacing(5)
        self.main_layout.addLayout(rename_mult_layout)
        self._rename_mult_cbx = QCheckBox()
        self._rename_mult_cbx.setChecked(True)
        self._rename_mult_method_lbl = QLabel('Mult. Naming: ')
        self._renamer_mult_method_combo = QComboBox()
        self._renamer_mult_method_combo.addItem('Numbers (0-9)')
        self._renamer_mult_method_combo.addItem('Letters (a-z)')
        rename_mult_layout.addWidget(self._rename_mult_cbx)
        rename_mult_layout.addWidget(self._rename_mult_method_lbl)
        rename_mult_layout.addWidget(self._renamer_mult_method_combo)
        self._frame_pad_lbl = QLabel('No. Padding: ')
        self._frame_pad_spin = QSpinBox()
        self._frame_pad_spin.setValue(2)
        self._frame_pad_spin.setFocusPolicy(Qt.NoFocus)
        self._frame_pad_spin.setMinimum(0)
        self._frame_pad_spin.setMaximum(10)
        self._frame_combo = QComboBox()
        self._frame_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._frame_combo.addItems(['Replace', 'Append', 'Change Pad'])
        self._frame_btn = QPushButton()
        self._frame_btn.setIcon(tpDcc.ResourcesMgr().icon('numbered_list'))
        rename_mult_layout.addWidget(self._frame_pad_lbl)
        rename_mult_layout.addWidget(self._frame_pad_spin)
        rename_mult_layout.addWidget(self._frame_combo)
        rename_mult_layout.addWidget(self._frame_btn)
        lower_upper_grp = QButtonGroup(self)
        self._lower_radio = QRadioButton('Lower')
        self._upper_radio = QRadioButton('Upper')
        lower_upper_grp.addButton(self._lower_radio)
        lower_upper_grp.addButton(self._upper_radio)
        self._lower_radio.setVisible(False)
        self._upper_radio.setVisible(False)
        self._lower_radio.setFixedHeight(19)
        self._upper_radio.setFixedHeight(19)
        self._upper_radio.setAutoExclusive(True)
        self._lower_radio.setAutoExclusive(True)
        self._lower_radio.setChecked(True)
        self._lower_radio.setEnabled(False)
        self._upper_radio.setEnabled(False)
        rename_mult_layout.addWidget(self._lower_radio)
        rename_mult_layout.addWidget(self._upper_radio)

        self.main_layout.addLayout(splitters.SplitterLayout())

        side_layout = QHBoxLayout()
        side_layout.setAlignment(Qt.AlignLeft)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(2)
        self.main_layout.addLayout(side_layout)
        self._side_cbx = QCheckBox()
        self._side_cbx.setChecked(True)
        side_layout.addWidget(self._side_cbx)
        side_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._side_lbl = QLabel('Side: ')
        self._none_side = QRadioButton('None')
        self._right_side = QRadioButton('Right')
        self._center_side = QRadioButton('Center')
        self._mid_side = QRadioButton('Mid')
        self._left_side = QRadioButton('Left')
        self._none_side.setFixedHeight(15)
        self._right_side.setFixedHeight(15)
        self._center_side.setFixedHeight(15)
        self._mid_side.setFixedHeight(15)
        self._left_side.setFixedHeight(15)
        side_layout.addWidget(self._side_lbl)
        side_layout.addWidget(self._none_side)
        side_layout.addWidget(self._right_side)
        side_layout.addWidget(self._center_side)
        side_layout.addWidget(self._mid_side)
        side_layout.addWidget(self._left_side)
        self._none_side.setAutoExclusive(True)
        self._right_side.setAutoExclusive(True)
        self._center_side.setAutoExclusive(True)
        self._mid_side.setAutoExclusive(True)
        self._left_side.setAutoExclusive(True)
        self._none_side.setChecked(True)
        self._capital_side = QCheckBox('Capital?')
        self._side_btn = QPushButton()
        self._side_btn.setIcon(tpDcc.ResourcesMgr().icon('font_size'))
        side_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        side_layout.addWidget(self._capital_side)
        side_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        side_layout.addWidget(self._side_btn)

    def setup_signals(self):
        self._rename_mult_cbx.toggled.connect(self._on_mult_naming_toggled)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._on_toggle_mult_naming_method)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._on_mult_method_combo_index_changed)
        self._upper_radio.clicked.connect(self._on_upper_lower_radio_clicked)
        self._lower_radio.clicked.connect(self._on_upper_lower_radio_clicked)
        self._frame_pad_spin.valueChanged.connect(self._on_padding_spinner_value_changed)
        self._frame_btn.clicked.connect(self._on_pad)

        self._side_cbx.toggled.connect(self._on_side_toggled)
        self._none_side.clicked.connect(self._on_side_radio_clcked)
        self._center_side.clicked.connect(self._on_side_radio_clcked)
        self._mid_side.clicked.connect(self._on_side_radio_clcked)
        self._left_side.clicked.connect(self._on_side_radio_clcked)
        self._right_side.clicked.connect(self._on_side_radio_clcked)
        self._capital_side.toggled.connect(self._on_side_radio_clcked)
        self._side_btn.clicked.connect(self._on_side)

    def get_rename_settings(self):
        """
        :return:
        """

        naming_method = bool(self._renamer_mult_method_combo.currentIndex())
        padding = 0
        upper = True

        if not naming_method:
            padding = self._frame_pad_spin.value()
        else:
            upper = self._upper_radio.isChecked()

        side = self._get_selected_side()

        return padding, naming_method, upper, side

    def _get_selected_side(self):

        side = ''
        if not self._side_cbx.isChecked():
            side = ''
        else:
            if self._none_side.isChecked():
                side = ''
            if self._right_side.isChecked():
                if self._capital_side.isChecked():
                    side = 'R'
                else:
                    side = 'r'
            if self._center_side.isChecked():
                if self._capital_side.isChecked():
                    side = 'C'
                else:
                    side = 'c'
            if self._mid_side.isChecked():
                if self._capital_side.isChecked():
                    side = 'M'
                else:
                    side = 'm'
            if self._left_side.isChecked():
                if self._capital_side.isChecked():
                    side = 'L'
                else:
                    side = 'l'

        return side

    def _on_mult_naming_toggled(self, flag):
        self._rename_mult_method_lbl.setEnabled(flag)
        self._renamer_mult_method_combo.setEnabled(flag)
        self._frame_pad_lbl.setEnabled(flag)
        self._frame_pad_spin.setEnabled(flag)
        self._frame_combo.setEnabled(flag)
        self._frame_btn.setEnabled(flag)
        self._lower_radio.setEnabled(flag)
        self._upper_radio.setEnabled(flag)

    def _on_toggle_mult_naming_method(self, index):
        """
        Method that updates the status of the radio buttons considering which option es enabled
        """

        self._lower_radio.setVisible(index)
        self._upper_radio.setVisible(index)
        self._frame_pad_lbl.setVisible(not index)
        self._frame_pad_spin.setVisible(not index)

    def _on_side_toggled(self, flag):
        self._side_lbl.setEnabled(flag)
        self._none_side.setEnabled(flag)
        self._center_side.setEnabled(flag)
        self._left_side.setEnabled(flag)
        self._right_side.setEnabled(flag)
        self._mid_side.setEnabled(flag)
        self._capital_side.setEnabled(flag)
        self._side_btn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_mult_method_combo_index_changed(self):
        self.renameUpdate.emit()

    def _on_upper_lower_radio_clicked(self):
        self.renameUpdate.emit()

    def _on_padding_spinner_value_changed(self):
        self.renameUpdate.emit()

    def _on_pad(self):
        pad_operation_index = self._frame_combo.currentIndex()
        if pad_operation_index == 0:
            self.doReplacePadding.emit(self._frame_pad_spin.value())
        elif pad_operation_index == 1:
            self.doAppendPadding.emit(self._frame_pad_spin.value())
        elif pad_operation_index == 2:
            self.doChangePadding.emit(self._frame_pad_spin.value())

    def _on_side_radio_clcked(self):
        self.renameUpdate.emit()

    def _on_side(self):
        selected_side = self._get_selected_side()
        self.doSide.emit(selected_side)
