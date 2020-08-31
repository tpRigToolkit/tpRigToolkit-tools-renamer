#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages index rename functionality
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, dividers, label, buttons, checkbox, combobox, spinbox


class NumberSideView(base.BaseWidget, object):

    # renameUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(NumberSideView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(NumberSideView, self).ui()

        rename_mult_layout = layouts.HorizontalLayout(spacing=5, margins=(0, 0, 0, 0))
        rename_mult_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(rename_mult_layout)
        self._rename_mult_cbx = checkbox.BaseCheckBox(parent=self)
        self._rename_mult_cbx.setChecked(True)
        self._rename_mult_method_lbl = label.BaseLabel('Mult. Naming: ', parent=self)
        self._renamer_mult_method_combo = combobox.BaseComboBox(parent=self)
        self._renamer_mult_method_combo.addItem('Numbers (0-9)')
        self._renamer_mult_method_combo.addItem('Letters (a-z)')
        rename_mult_layout.addWidget(self._rename_mult_cbx)
        rename_mult_layout.addWidget(self._rename_mult_method_lbl)
        rename_mult_layout.addWidget(self._renamer_mult_method_combo)
        self._frame_pad_lbl = label.BaseLabel('No. Padding: ', parent=self)
        self._frame_pad_spin = spinbox.BaseSpinBox(parent=self)
        self._frame_pad_spin.setValue(2)
        self._frame_pad_spin.setFocusPolicy(Qt.NoFocus)
        self._frame_pad_spin.setMinimum(1)
        self._frame_pad_spin.setMaximum(10)
        self._frame_combo = combobox.BaseComboBox(parent=self)
        self._frame_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._frame_combo.addItems(['Replace', 'Append', 'Change Pad'])
        self._frame_btn = buttons.BaseButton()
        self._frame_btn.setIcon(tp.ResourcesMgr().icon('numbered_list'))
        rename_mult_layout.addWidget(self._frame_pad_lbl)
        rename_mult_layout.addWidget(self._frame_pad_spin)
        rename_mult_layout.addWidget(self._frame_combo)
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
        rename_mult_layout.addWidget(self._frame_btn)

        self.main_layout.addLayout(dividers.DividerLayout())

        side_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        side_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(side_layout)
        self._side_cbx = checkbox.BaseCheckBox(parent=self)
        self._side_cbx.setChecked(True)
        side_layout.addWidget(self._side_cbx)
        self._side_lbl = label.BaseLabel('Side: ', parent=self)
        self._none_side = buttons.BaseRadioButton('None', parent=self)
        self._right_side = buttons.BaseRadioButton('Right', parent=self)
        self._center_side = buttons.BaseRadioButton('Center', parent=self)
        self._mid_side = buttons.BaseRadioButton('Mid', parent=self)
        self._left_side = buttons.BaseRadioButton('Left', parent=self)
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
        self._capital_side = checkbox.BaseCheckBox('Capital?', parent=self)
        self._side_btn = buttons.BaseButton(parent=self)
        self._side_btn.setIcon(tp.ResourcesMgr().icon('font_size'))
        side_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        side_layout.addWidget(self._capital_side)
        side_layout.addItem(QSpacerItem(15, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        side_layout.addWidget(self._side_btn)

    def setup_signals(self):

        self._rename_mult_cbx.toggled.connect(self._on_mult_naming_toggled)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._on_toggle_mult_naming_method)
        self._side_cbx.toggled.connect(self._on_side_toggled)

        self._rename_mult_cbx.toggled.connect(self._controller.toggle_rename_multiple_check)
        self._renamer_mult_method_combo.currentIndexChanged.connect(self._controller.change_multiple_naming_index)
        self._frame_pad_spin.valueChanged.connect(self._controller.change_padding_value)
        self._frame_combo.currentIndexChanged.connect(self._controller.change_padding_option)
        self._lower_radio.clicked.connect(partial(self._controller.change_letter_type, 0))
        self._upper_radio.clicked.connect(partial(self._controller.change_letter_type, 1))
        self._side_cbx.toggled.connect(self._controller.toggle_side)
        self._none_side.clicked.connect(partial(self._controller.change_side, 0))
        self._right_side.clicked.connect(partial(self._controller.change_side, 1))
        self._center_side.clicked.connect(partial(self._controller.change_side, 2))
        self._mid_side.clicked.connect(partial(self._controller.change_side, 3))
        self._left_side.clicked.connect(partial(self._controller.change_side, 4))
        self._capital_side.toggled.connect(self._controller.toggle_capital_side)
        self._frame_btn.clicked.connect(self._controller.rename_padding)
        self._side_btn.clicked.connect(self._controller.add_side)

        self._model.multipleNamingCheckChanged.connect(self._rename_mult_cbx.setChecked)
        self._model.multipleIndexChanged.connect(self._renamer_mult_method_combo.setCurrentIndex)
        self._model.paddingValueChanged.connect(self._frame_pad_spin.setValue)
        self._model.paddingOptionChanged.connect(self._frame_combo.setCurrentIndex)
        self._model.letterTypeChanged.connect(self._on_letter_type_changed)
        self._model.sideCheckChanged.connect(self._side_cbx.setChecked)
        self._model.sideChanged.connect(self._on_side_changed)
        self._model.capitalCheckChanged.connect(self._capital_side.setChecked)

    def refresh(self):
        self._rename_mult_cbx.setChecked(self._model.multiple_naming_check)
        self._renamer_mult_method_combo.setCurrentIndex(self._model.multiple_naming_index)
        self._frame_pad_spin.setValue(self._model.padding_value)
        self._frame_combo.setCurrentIndex(self._model.padding_option)
        self._side_cbx.setChecked(self._model.side_check)
        self._capital_side.setChecked(self._model.capital_check)

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
        self._on_mult_naming_toggled(self._rename_mult_cbx.isChecked())

    def _on_side_toggled(self, flag):
        self._side_lbl.setEnabled(flag)
        self._none_side.setEnabled(flag)
        self._center_side.setEnabled(flag)
        self._left_side.setEnabled(flag)
        self._right_side.setEnabled(flag)
        self._mid_side.setEnabled(flag)
        self._capital_side.setEnabled(flag)
        self._side_btn.setEnabled(flag)
        # self.renameUpdate.emit()

    def _on_letter_type_changed(self, index):
        if index == 0:
            self._lower_radio.setChecked(True)
        else:
            self._upper_radio.setChecked(True)

    def _on_side_changed(self, index):
        if index == 0:
            self._none_side.setChecked(True)
        elif index == 1:
            self._right_side.setChecked(True)
        elif index == 2:
            self._center_side.setChecked(True)
        elif index == 3:
            self._mid_side.setChecked(True)
        else:
            self._left_side.setChecked(True)


class NumberSideWidgetModel(QObject, object):

    multipleNamingCheckChanged = Signal(bool)
    multipleIndexChanged = Signal(int)
    paddingValueChanged = Signal(int)
    paddingOptionChanged = Signal(int)
    letterTypeChanged = Signal(int)
    sideCheckChanged = Signal(bool)
    sideChanged = Signal(int)
    capitalCheckChanged = Signal(bool)

    def __init__(self):
        super(NumberSideWidgetModel, self).__init__()

        self._global_data = dict()
        self._multiple_naming_check = True
        self._multiple_naming_index = 0
        self._padding_value = 2
        self._padding_option = 0
        self._letter_type = 0
        self._side_check = True
        self._side = 0
        self._capital_check = False

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict

    @property
    def multiple_naming_check(self):
        return self._multiple_naming_check

    @multiple_naming_check.setter
    def multiple_naming_check(self, flag):
        self._multiple_naming_check = bool(flag)
        self.multipleNamingCheckChanged.emit(self._multiple_naming_check)

    @property
    def multiple_naming_index(self):
        return self._multiple_naming_index

    @multiple_naming_index.setter
    def multiple_naming_index(self, value):
        self._multiple_naming_index = int(value)
        self.multipleIndexChanged.emit(self._multiple_naming_index)

    @property
    def padding_value(self):
        return self._padding_value

    @padding_value.setter
    def padding_value(self, value):
        self._padding_value = int(value)
        self.paddingValueChanged.emit(self._padding_value)

    @property
    def padding_option(self):
        return self._padding_option

    @padding_option.setter
    def padding_option(self, value):
        self._padding_option = int(value)
        self.paddingOptionChanged.emit(self._padding_option)

    @property
    def letter_type(self):
        return self._letter_type

    @letter_type.setter
    def letter_type(self, index):
        self._letter_type = int(index)
        self.letterTypeChanged.emit(self._letter_type)

    @property
    def side_check(self):
        return self._side_check

    @side_check.setter
    def side_check(self, flag):
        self._side_check = flag
        self.sideCheckChanged.emit(flag)

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, value):
        self._side = int(value)
        self.sideChanged.emit(self._side)

    @property
    def capital_check(self):
        return self._capital_check

    @capital_check.setter
    def capital_check(self, flag):
        self._capital_check = bool(flag)
        self.capitalCheckChanged.emit(self._capital_check)

    def get_side(self):
        side_index = self.side
        side_capital = self.capital_check

        side = ''
        if side_index == 0 or not self.side_check:
            return ''
        else:
            if side_index == 1:
                side = 'r' if not side_capital else 'R'
            elif side_index == 2:
                side = 'c' if not side_capital else 'C'
            elif side_index == 3:
                side = 'm' if not side_capital else 'M'
            elif side_index == 4:
                side = 'l' if not side_capital else 'L'

        return side

    @property
    def rename_settings(self):
        naming_method = self.multiple_naming_index
        padding = 0
        upper = True

        if not naming_method:
            padding = self.padding_value
        else:
            upper = self.letter_type == 1

        side = self.get_side()

        return {
            'padding': padding,
            'naming_method': naming_method,
            'upper': upper,
            'side': side
        }


class NumberSideWidgetController(object):
    def __init__(self, client, model):
        super(NumberSideWidgetController, self).__init__()

        self._client = client
        self._model = model

    def toggle_rename_multiple_check(self, flag):
        self._model.multiple_naming_check = flag

    def change_multiple_naming_index(self, index):
        self._model.multiple_naming_index = index

    def change_padding_value(self, value):
        self._model.padding_value = value

    def change_padding_option(self, index):
        self._model.padding_option = index

    def toggle_side(self, flag):
        self._model.side_check = flag

    def change_side(self, index):
        self._model.side = index

    def toggle_capital_side(self, flag):
        self._model.capital_check = flag

    def change_letter_type(self, index):
        self._model.letter_type = index

    def rename_padding(self):
        padding_option = self._model.padding_option
        if padding_option == 0:
            self.replace_padding()
        elif padding_option == 1:
            self.append_padding()
        elif padding_option == 2:
            self.change_padding()

    @tp.Dcc.get_undo_decorator()
    def replace_padding(self):
        global_data = self._model.global_data
        padding = self._model.padding_value
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.replace_padding(
            pad=padding, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def append_padding(self):
        global_data = self._model.global_data
        padding = self._model.padding_value
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.append_padding(
            pad=padding, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def change_padding(self):
        global_data = self._model.global_data
        padding = self._model.padding_value
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.change_padding(
            pad=padding, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def add_side(self):
        global_data = self._model.global_data
        side = self._model.get_side()
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        if not side:
            return

        return self._client.add_side(
            side=side, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )


def number_side_widget(client, parent=None):

    model = NumberSideWidgetModel()
    controller = NumberSideWidgetController(client=client, model=model)
    view = NumberSideView(model=model, controller=controller, parent=parent)

    return view
