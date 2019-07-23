#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages basic rename functionality for tpRenamer
"""

from __future__ import print_function, division, absolute_import


from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from tpQtLib.core import base
from tpQtLib.widgets import splitters


class RenamerWidget(base.BaseWidget, object):

    renameUpdate = Signal()

    def __init__(self, parent=None):
        super(RenamerWidget, self).__init__(parent=parent)

    def ui(self):
        super(RenamerWidget, self).ui()

        self.main_layout.addWidget(splitters.Splitter('RENAME'))

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
        self._renamer_text_lbl = QLabel('New Name: ')
        self._renamer_line = QLineEdit()
        rename_layout.addWidget(self._renamer_text_lbl)
        rename_layout.addWidget(self._renamer_line)
        reg_ex = QRegExp("^(?!^_)[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._renamer_line)
        self._renamer_line.setValidator(text_validator)
        self._renamer_text_lbl.setEnabled(False)
        self._renamer_line.setEnabled(False)

        rename_mult_layout = QHBoxLayout()
        rename_mult_layout.setAlignment(Qt.AlignLeft)
        rename_mult_layout.setContentsMargins(0, 0, 0, 0)
        rename_mult_layout.setSpacing(5)
        renamer_widget.layout().addLayout(rename_mult_layout)
        rename_mult_layout.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        rename_mult_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._rename_mult_method_lbl = QLabel('Mult. Naming: ')
        self._renamer_mult_method_combo = QComboBox()
        self._renamer_mult_method_combo.addItem('Numbers (0-9)')
        self._renamer_mult_method_combo.addItem('Letters (a-z)')
        self._renamer_mult_method_combo.setFixedWidth(100)
        rename_mult_layout.addWidget(self._rename_mult_method_lbl)
        rename_mult_layout.addWidget(self._renamer_mult_method_combo)
        self._rename_mult_method_lbl.setEnabled(False)
        self._renamer_mult_method_combo.setEnabled(False)
        self._frame_pad_lbl = QLabel('No. Padding: ')
        self._frame_pad_spin = QSpinBox()
        self._frame_pad_spin.setFocusPolicy(Qt.NoFocus)
        self._frame_pad_spin.setFixedWidth(40)
        self._frame_pad_spin.setMinimum(0)
        self._frame_pad_spin.setMaximum(10)
        self._frame_pad_lbl.setEnabled(False)
        self._frame_pad_spin.setEnabled(False)
        rename_mult_layout.addWidget(self._frame_pad_lbl)
        rename_mult_layout.addWidget(self._frame_pad_spin)
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

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        side_layout = QHBoxLayout()
        side_layout.setAlignment(Qt.AlignLeft)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(2)
        renamer_widget.layout().addLayout(side_layout)
        self._side_cbx = QCheckBox()
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
        self._side_lbl.setEnabled(False)
        self._none_side.setEnabled(False)
        self._right_side.setEnabled(False)
        self._center_side.setEnabled(False)
        self._mid_side.setEnabled(False)
        self._left_side.setEnabled(False)

        side_layout2 = QHBoxLayout()
        side_layout2.setAlignment(Qt.AlignLeft)
        side_layout2.setContentsMargins(0, 0, 0, 0)
        side_layout2.setSpacing(2)
        renamer_widget.layout().addLayout(side_layout2)
        self._capital_side = QCheckBox('Capital?')
        side_layout2.addItem(QSpacerItem(25, 0, QSizePolicy.Fixed, QSizePolicy.Preferred))
        side_layout2.addWidget(splitters.get_horizontal_separator_widget())
        side_layout2.addWidget(self._capital_side)
        self._capital_side.setEnabled(False)

        last_joint_layout = QHBoxLayout()
        last_joint_layout.setAlignment(Qt.AlignLeft)
        last_joint_layout.setContentsMargins(0, 0, 0, 0)
        last_joint_layout.setSpacing(2)
        renamer_widget.layout().addLayout(last_joint_layout)
        self._last_joint_is_end_cbx = QCheckBox()
        self._last_joint_is_end_lbl = QLabel('Last joint is an endJoint?')
        self._last_joint_is_end_cbx.setChecked(True)
        last_joint_layout.addWidget(self._last_joint_is_end_cbx)
        last_joint_layout.addWidget(splitters.get_horizontal_separator_widget())
        last_joint_layout.addWidget(self._last_joint_is_end_lbl)

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        prefix_layout = QHBoxLayout()
        prefix_layout.setAlignment(Qt.AlignLeft)
        prefix_layout.setContentsMargins(0, 0, 0, 0)
        prefix_layout.setSpacing(2)
        renamer_widget.layout().addLayout(prefix_layout)
        self._prefix_cbx = QCheckBox()
        prefix_layout.addWidget(self._prefix_cbx)
        prefix_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._prefix_lbl = QLabel('Prefix: ')
        self._prefix_line = QLineEdit()
        self._prefix_line.setEnabled(False)
        self._prefix_line.setValidator(text_validator)
        prefix_layout.addWidget(self._prefix_lbl)
        prefix_layout.addWidget(self._prefix_line)
        self._prefix_lbl.setEnabled(False)
        self._prefix_line.setEnabled(False)

        remove_first_layout = QHBoxLayout()
        remove_first_layout.setAlignment(Qt.AlignLeft)
        remove_first_layout.setContentsMargins(0, 0, 0, 0)
        remove_first_layout.setSpacing(2)
        renamer_widget.layout().addLayout(remove_first_layout)
        self._remove_first_cbx = QCheckBox()
        remove_first_layout.addWidget(self._remove_first_cbx)
        remove_first_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._remove_first_lbl = QLabel('Remove first: ')
        self._remove_first_spn = QSpinBox()
        self._remove_first_spn.setFocusPolicy(Qt.NoFocus)
        self._remove_first_spn.setFixedWidth(40)
        self._remove_first_spn.setMinimum(0)
        self._remove_first_spn.setMaximum(99)
        last_digits_lbl = QLabel(' digits')
        remove_first_layout.addWidget(self._remove_first_lbl)
        remove_first_layout.addWidget(self._remove_first_spn)
        remove_first_layout.addWidget(last_digits_lbl)
        self._remove_first_lbl.setEnabled(False)
        self._remove_first_spn.setEnabled(False)

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        suffix_layout = QHBoxLayout()
        suffix_layout.setAlignment(Qt.AlignLeft)
        suffix_layout.setContentsMargins(0, 0, 0, 0)
        suffix_layout.setSpacing(2)
        renamer_widget.layout().addLayout(suffix_layout)
        self._suffix_cbx = QCheckBox()
        suffix_layout.addWidget(self._suffix_cbx)
        suffix_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._suffix_lbl = QLabel('Suffix: ')
        self._suffix_line = QLineEdit()
        self._suffix_line.setEnabled(False)
        self._suffix_line.setValidator(text_validator)
        suffix_layout.addWidget(self._suffix_lbl)
        suffix_layout.addWidget(self._suffix_line)
        self._suffix_lbl.setEnabled(False)
        self._suffix_line.setEnabled(False)

        remove_last_layout = QHBoxLayout()
        remove_last_layout.setAlignment(Qt.AlignLeft)
        remove_last_layout.setContentsMargins(0, 0, 0, 0)
        remove_last_layout.setSpacing(2)
        renamer_widget.layout().addLayout(remove_last_layout)
        self._remove_last_cbx = QCheckBox()
        remove_last_layout.addWidget(self._remove_last_cbx)
        remove_last_layout.addWidget(splitters.get_horizontal_separator_widget())
        self._remove_last_lbl = QLabel('Remove last: ')
        self._remove_last_spn = QSpinBox()
        self._remove_last_spn.setFocusPolicy(Qt.NoFocus)
        self._remove_last_spn.setFixedWidth(40)
        self._remove_last_spn.setMinimum(0)
        self._remove_last_spn.setMaximum(99)
        last_digits_lbl2 = QLabel(' digits')
        remove_last_layout.addWidget(self._remove_last_lbl)
        remove_last_layout.addWidget(self._remove_last_spn)
        remove_last_layout.addWidget(last_digits_lbl2)
        self._remove_last_lbl.setEnabled(False)
        self._remove_last_spn.setEnabled(False)

    def setup_signals(self):
        self._base_name_cbx.toggled.connect(self._on_base_name_toggled)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._on_toggle_mult_naming_method)
        self._renamer_line.textChanged.connect(self._on_rename_line_text_changed)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._on_mult_method_combo_index_changed)
        self._upper_radio.clicked.connect(self._on_upper_lower_radio_clicked)
        self._lower_radio.clicked.connect(self._on_upper_lower_radio_clicked)
        self._frame_pad_spin.valueChanged.connect(self._on_padding_spinner_value_changed)

        self._side_cbx.toggled.connect(self._on_side_toggled)
        self._none_side.clicked.connect(self._on_side_radio_clcked)
        self._center_side.clicked.connect(self._on_side_radio_clcked)
        self._mid_side.clicked.connect(self._on_side_radio_clcked)
        self._left_side.clicked.connect(self._on_side_radio_clcked)
        self._right_side.clicked.connect(self._on_side_radio_clcked)
        self._capital_side.toggled.connect(self._on_side_radio_clcked)

        self._prefix_cbx.toggled.connect(self._on_prefix_toggled)
        self._prefix_line.textChanged.connect(self._on_prefx_line_text_changed)

        self._remove_first_cbx.toggled.connect(self._on_remove_first_toggled)
        self._remove_first_spn.valueChanged.connect(self._on_remove_first_value_changed)

        self._suffix_cbx.toggled.connect(self._on_suffix_toggled)
        self._suffix_line.textChanged.connect(self._on_suffix_line_text_changed)

        self._remove_last_cbx.toggled.connect(self._on_remove_last_toggled)
        self._remove_last_spn.valueChanged.connect(self._on_remove_last_value_changed)

    def get_rename_settings(self):
        """
        Internal function that returns current rename settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        if self._base_name_cbx.isChecked():
            text = str(self._renamer_line.text()).strip()
        else:
            text = ''

        naming_method = bool(self._renamer_mult_method_combo.currentIndex())
        padding = 0
        upper = True

        if not naming_method:
            padding = self._frame_pad_spin.value()
        else:
            upper = self._upper_radio.isChecked()

        prefix = ''
        suffix = ''

        if self._prefix_cbx.isChecked():
            prefix = self._prefix_line.text()
        if self._suffix_cbx.isChecked():
            suffix = self._suffix_line.text()

        if not self._side_cbx.isChecked():
            side  = None
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

        if not self._remove_first_cbx.isChecked():
            remove_first = 0
        else:
            remove_first = self._remove_first_spn.value()

        if not self._remove_last_cbx.isChecked():
            remove_last = 0
        else:
            remove_last = self._remove_last_spn.value()

        joint_end = self._last_joint_is_end_cbx.isChecked()

        return text, prefix, suffix, padding, naming_method, upper, side, remove_first, remove_last, joint_end

    def _on_base_name_toggled(self, flag):
        self._renamer_text_lbl.setEnabled(flag)
        self._renamer_line.setEnabled(flag)
        self._rename_mult_method_lbl.setEnabled(flag)
        self._renamer_mult_method_combo.setEnabled(flag)
        self._frame_pad_lbl.setEnabled(flag)
        self._frame_pad_spin.setEnabled(flag)
        self._lower_radio.setEnabled(flag)
        self._upper_radio.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_side_toggled(self, flag):
        self._side_lbl.setEnabled(flag)
        self._none_side.setEnabled(flag)
        self._center_side.setEnabled(flag)
        self._left_side.setEnabled(flag)
        self._right_side.setEnabled(flag)
        self._mid_side.setEnabled(flag)
        self._capital_side.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_prefix_toggled(self, flag):
        self._prefix_lbl.setEnabled(flag)
        self._prefix_line.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_remove_first_toggled(self, flag):
        self._remove_first_lbl.setEnabled(flag)
        self._remove_first_spn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_suffix_toggled(self, flag):
        self._suffix_lbl.setEnabled(flag)
        self._suffix_line.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_remove_last_toggled(self, flag):
        self._remove_last_lbl.setEnabled(flag)
        self._remove_last_spn.setEnabled(flag)
        self.renameUpdate.emit()

    def _on_toggle_mult_naming_method(self, index):

        """
        Method that updates the status of the radio buttons considering which option es enabled
        """

        self._lower_radio.setVisible(index)
        self._upper_radio.setVisible(index)
        self._frame_pad_lbl.setVisible(not index)
        self._frame_pad_spin.setVisible(not index)

    def _on_rename_line_text_changed(self, new_text):
        self.renameUpdate.emit()

    def _on_mult_method_combo_index_changed(self, index):
        self.renameUpdate.emit()

    def _on_upper_lower_radio_clicked(self):
        self.renameUpdate.emit()

    def _on_padding_spinner_value_changed(self, value):
        self.renameUpdate.emit()

    def _on_side_radio_clcked(self):
        self.renameUpdate.emit()

    def _on_prefx_line_text_changed(self, new_text):
        self.renameUpdate.emit()

    def _on_suffix_line_text_changed(self, new_text):
        self.renameUpdate.emit()

    def _on_remove_first_value_changed(self, value):
        self.renameUpdate.emit()

    def _on_remove_last_value_changed(self, value):
        self.renameUpdate.emit()
