#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages prefix/suffix rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, dividers, label, buttons, checkbox, lineedit, combobox, spinbox


class PrefixSuffixView(base.BaseWidget, object):

    # renameUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(PrefixSuffixView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(PrefixSuffixView, self).ui()

        prefix_layout = layouts.HorizontalLayout(spacing=5, margins=(0, 0, 0, 0))
        prefix_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(prefix_layout)
        self._prefix_cbx = checkbox.BaseCheckBox(parent=self)
        prefix_layout.addWidget(self._prefix_cbx)
        self._prefix_line = lineedit.BaseLineEdit(parent=self)
        self._prefix_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._prefix_line.setPlaceholderText('Prefix')
        prefix_reg_exp = QRegExp("^(?!^_)[a-zA-Z_]+")
        prefix_validator = QRegExpValidator(prefix_reg_exp, self._prefix_line)
        self._prefix_line.setValidator(prefix_validator)
        self._prefix_combo = combobox.BaseComboBox(parent=self)
        self._prefix_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        prefix_layout.addWidget(self._prefix_line)
        prefix_layout.addWidget(self._prefix_combo)
        self._prefix_btn = buttons.BaseButton(parent=self)
        self._prefix_btn.setIcon(tp.ResourcesMgr().icon('prefix'))
        self._remove_prefix_btn = buttons.BaseButton(parent=self)
        self._remove_prefix_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        prefix_layout.addWidget(self._prefix_btn)
        prefix_layout.addWidget(self._remove_prefix_btn)

        remove_first_layout = layouts.HorizontalLayout(spacing=2, margins=(0, 0, 0, 0))
        remove_first_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(remove_first_layout)
        self._remove_first_cbx = checkbox.BaseCheckBox(parent=self)
        remove_first_layout.addWidget(self._remove_first_cbx)
        self._remove_first_lbl = label.BaseLabel('Remove first: ')
        self._remove_first_spn = spinbox.BaseSpinBox(parent=self)
        self._remove_first_spn.setFocusPolicy(Qt.NoFocus)
        self._remove_first_spn.setMinimum(0)
        self._remove_first_spn.setMaximum(99)
        last_digits_lbl = QLabel(' digits', parent=self)
        remove_first_layout.addWidget(self._remove_first_lbl)
        remove_first_layout.addWidget(self._remove_first_spn)
        remove_first_layout.addWidget(last_digits_lbl)
        self._remove_first_btn = buttons.BaseButton(parent=self)
        self._remove_first_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        remove_first_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        remove_first_layout.addWidget(self._remove_first_btn)

        self.main_layout.addWidget(dividers.Divider(parent=self))

        suffix_layout = layouts.HorizontalLayout(spacing=5, margins=(0, 0, 0, 0))
        suffix_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(suffix_layout)
        self._suffix_cbx = checkbox.BaseCheckBox(parent=self)
        suffix_layout.addWidget(self._suffix_cbx)
        self._suffix_line = lineedit.BaseLineEdit(parent=self)
        self._suffix_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        suffix_reg_exp = QRegExp("^[a-zA-Z_0-9]+")
        suffix_validator = QRegExpValidator(suffix_reg_exp, self._suffix_line)
        self._suffix_line.setValidator(suffix_validator)
        self._suffix_line.setPlaceholderText('Suffix')
        self._suffix_combo = combobox.BaseComboBox(parent=self)
        self._suffix_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        suffix_layout.addWidget(self._suffix_line)
        suffix_layout.addWidget(self._suffix_combo)
        self._suffix_btn = buttons.BaseButton(parent=self)
        self._suffix_btn.setIcon(tp.ResourcesMgr().icon('suffix'))
        self._remove_suffix_btn = buttons.BaseButton(parent=self)
        self._remove_suffix_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        suffix_layout.addWidget(self._suffix_btn)
        suffix_layout.addWidget(self._remove_suffix_btn)

        remove_last_layout = layouts.HorizontalLayout(spacing=5, margins=(0, 0, 0, 0))
        remove_last_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addLayout(remove_last_layout)
        self._remove_last_cbx = checkbox.BaseCheckBox(parent=self)
        remove_last_layout.addWidget(self._remove_last_cbx)
        self._remove_last_lbl = label.BaseLabel('Remove last: ', parent=self)
        self._remove_last_spn = spinbox.BaseSpinBox(parent=self)
        self._remove_last_spn.setFocusPolicy(Qt.NoFocus)
        self._remove_last_spn.setMinimum(0)
        self._remove_last_spn.setMaximum(99)
        last_digits_lbl2 = label.BaseLabel(' digits', parent=None)
        remove_last_layout.addWidget(self._remove_last_lbl)
        remove_last_layout.addWidget(self._remove_last_spn)
        remove_last_layout.addWidget(last_digits_lbl2)
        self._remove_last_btn = buttons.BaseButton()
        self._remove_last_btn.setIcon(tp.ResourcesMgr().icon('trash'))
        remove_last_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Preferred))
        remove_last_layout.addWidget(self._remove_last_btn)

        # last_joint_layout = QHBoxLayout()
        # last_joint_layout.setAlignment(Qt.AlignLeft)
        # last_joint_layout.setContentsMargins(0, 0, 0, 0)
        # last_joint_layout.setSpacing(2)
        # self.main_layout.addLayout(last_joint_layout)
        # self._last_joint_is_end_cbx = QCheckBox()
        # self._last_joint_is_end_lbl = QLabel('Last joint is an endJoint?')
        # self._last_joint_is_end_cbx.setChecked(True)
        # last_joint_layout.addWidget(self._last_joint_is_end_cbx)
        # last_joint_layout.addWidget(dividers.get_horizontal_separator_widget())
        # last_joint_layout.addWidget(self._last_joint_is_end_lbl)

    def setup_signals(self):

        self._prefix_cbx.toggled.connect(self._controller.toggle_prefix_check)
        self._prefix_line.textChanged.connect(self._controller.change_prefix)
        self._remove_first_cbx.toggled.connect(self._controller.toggle_remove_first)
        self._remove_first_spn.valueChanged.connect(self._controller.change_remove_first_value)
        self._prefix_btn.clicked.connect(self._controller.add_prefix)
        self._remove_prefix_btn.clicked.connect(self._controller.remove_prefix)
        self._remove_first_btn.clicked.connect(self._controller.remove_first)
        self._suffix_cbx.toggled.connect(self._controller.toggle_suffix_check)
        self._suffix_line.textChanged.connect(self._controller.change_suffix)
        self._suffix_btn.clicked.connect(self._controller.add_suffix)
        self._remove_suffix_btn.clicked.connect(self._controller.remove_suffix)
        self._remove_last_cbx.toggled.connect(self._controller.toggle_remove_last)
        self._remove_last_spn.valueChanged.connect(self._controller.change_remove_last_value)
        self._remove_last_btn.clicked.connect(self._controller.remove_last)
        self._prefix_combo.currentIndexChanged.connect(self._controller.change_selected_prefix)
        self._suffix_combo.currentIndexChanged.connect(self._controller.change_selected_suffix)

        self._model.prefixCheckChanged.connect(self._on_prefix_toggled)
        self._model.prefixChanged.connect(self._on_prefix_changed)
        self._model.removeFirstChanged.connect(self._on_remove_first_toggled)
        self._model.removeFirstValueChanged.connect(self._on_remove_first_value_changed)
        self._model.suffixCheckChanged.connect(self._on_suffix_toggled)
        self._model.suffixChanged.connect(self._on_suffix_changed)
        self._model.removeLastChanged.connect(self._on_remove_last_toggled)
        self._model.removeLastValueChanged.connect(self._on_remove_last_value_changed)
        self._model.selectedPrefixChanged.connect(self._on_selected_prefix_changed)
        self._model.selectedSuffixChanged.connect(self._on_selected_suffix_changed)

    def refresh(self):
        """
        Syncs view to the current state of its model
        """

        self._prefix_cbx.setChecked(self._model.prefix_check)
        self._prefix_line.setText(self._model.prefix)
        self._remove_first_cbx.setChecked(self._model.remove_first)
        self._remove_first_spn.setValue(self._model.remove_first_value)
        self._suffix_cbx.setChecked(self._model.suffix_check)
        self._suffix_line.setText(self._model.suffix)
        self._remove_first_cbx.setChecked(self._model.remove_last)
        self._remove_last_spn.setValue(self._model.remove_last_value)

        suffixes = self._model.suffixes
        self._prefix_combo.clear()
        self._suffix_combo.clear()
        self._prefix_combo.setVisible(bool(suffixes))
        self._suffix_combo.setVisible(bool(suffixes))

        if suffixes:
            self._prefix_combo.addItem('Select prefix ...')
            self._suffix_combo.addItem('Select suffix ...')
            format_items = ['{}: "{}"'.format(suffix.keys()[0], suffix.values()[0]) for suffix in suffixes]
            for i, item in enumerate(format_items):
                item_index = i + 1      # First index if selected prefix/suffix items ...
                self._prefix_combo.addItem(item)
                self._suffix_combo.addItem(item)
                self._prefix_combo.setItemData(item_index, suffixes[i].values()[0])
                self._suffix_combo.setItemData(item_index, suffixes[i].values()[0])

    #     self.renameUpdate.emit()

    # def get_rename_settings(self):
    #     """
    #     :return:
    #     """
    #
    #     prefix = ''
    #     suffix = ''
    #
    #     if self._prefix_cbx.isChecked():
    #         prefix = self._prefix_line.text()
    #     if self._suffix_cbx.isChecked():
    #         suffix = self._suffix_line.text()
    #
    #     if not self._remove_first_cbx.isChecked():
    #         remove_first = 0
    #     else:
    #         remove_first = self._remove_first_spn.value()
    #
    #     if not self._remove_last_cbx.isChecked():
    #         remove_last = 0
    #     else:
    #         remove_last = self._remove_last_spn.value()
    #
    #     joint_end = self._last_joint_is_end_cbx.isChecked()
    #
    #     return prefix, suffix, remove_first, remove_last, joint_end

    def _on_prefix_toggled(self, flag):
        self._prefix_cbx.setChecked(flag)
        self._prefix_line.setEnabled(flag)
        self._prefix_combo.setEnabled(flag)
        self._prefix_btn.setEnabled(flag)
        self._remove_prefix_btn.setEnabled(flag)
        # self.renameUpdate.emit()

    def _on_remove_first_toggled(self, flag):
        self._remove_first_cbx.setChecked(flag)
        self._remove_first_lbl.setEnabled(flag)
        self._remove_first_spn.setEnabled(flag)
        self._remove_first_btn.setEnabled(flag)
        # self.renameUpdate.emit()

    def _on_suffix_toggled(self, flag):
        self._suffix_cbx.setChecked(flag)
        self._suffix_line.setEnabled(flag)
        self._suffix_combo.setEnabled(flag)
        self._suffix_btn.setEnabled(flag)
        self._remove_suffix_btn.setEnabled(flag)
    #     self.renameUpdate.emit()

    def _on_remove_last_toggled(self, flag):
        self._remove_last_cbx.setChecked(flag)
        self._remove_last_lbl.setEnabled(flag)
        self._remove_last_spn.setEnabled(flag)
        self._remove_last_btn.setEnabled(flag)
    #     self.renameUpdate.emit()

    def _on_prefix_changed(self, new_prefix):
        self._prefix_line.setText(new_prefix)
        # self.renameUpdate.emit()

    def _on_suffix_changed(self, new_suffix):
        self._suffix_line.setText(new_suffix)
        # self.renameUpdate.emit()

    def _on_remove_first_value_changed(self, value):
        self._remove_first_spn.setValue(value)
        # self.renameUpdate.emit()

    def _on_remove_last_value_changed(self, value):
        self._remove_last_spn.setValue(value)
        # self.renameUpdate.emit()

    def _on_selected_prefix_changed(self, index):
        self._prefix_combo.setCurrentIndex(index)
        prefix_selected = self._prefix_combo.itemData(index)
        self._prefix_line.setText('{}_'.format(prefix_selected) if index > 0 else '')

    def _on_selected_suffix_changed(self, index):
        self._suffix_combo.setCurrentIndex(index)
        suffix_selected = self._suffix_combo.itemData(index)
        self._suffix_line.setText('{}_'.format(suffix_selected) if index > 0 else '')


class PrefixSuffixWidgetModel(QObject, object):

    prefixCheckChanged = Signal(bool)
    suffixCheckChanged = Signal(bool)
    prefixChanged = Signal(str)
    suffixChanged = Signal(str)
    removeFirstChanged = Signal(bool)
    removeFirstValueChanged = Signal(int)
    removeLastChanged = Signal(bool)
    removeLastValueChanged = Signal(int)
    selectedPrefixChanged = Signal(int)
    selectedSuffixChanged = Signal(int)

    def __init__(self, config):
        super(PrefixSuffixWidgetModel, self).__init__()

        self._global_data = dict()
        self._config = config
        self._prefix_check = True
        self._suffix_check = True
        self._prefix = ''
        self._suffix = ''
        self._selected_prefix = 0
        self._selected_suffix = 0
        self._remove_first = False
        self._remove_first_value = 3
        self._remove_last = False
        self._remove_last_value = 3

    @property
    def global_data(self):
        return self._global_data

    @global_data.setter
    def global_data(self, global_data_dict):
        self._global_data = global_data_dict

    @property
    def config(self):
        return self._config

    @property
    def prefix_check(self):
        return self._prefix_check

    @prefix_check.setter
    def prefix_check(self, flag):
        self._prefix_check = bool(flag)
        self.prefixCheckChanged.emit(self._prefix_check)

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = str(value)
        self.prefixChanged.emit(self._prefix)

    @property
    def remove_first(self):
        return self._remove_first

    @remove_first.setter
    def remove_first(self, flag):
        self._remove_first = bool(flag)
        self.removeFirstChanged.emit(self._remove_first)

    @property
    def remove_first_value(self):
        return self._remove_first_value

    @remove_first_value.setter
    def remove_first_value(self, value):
        self._remove_first_value = int(value)
        self.removeFirstValueChanged.emit(self._remove_first_value)

    @property
    def remove_last(self):
        return self._remove_last

    @remove_last.setter
    def remove_last(self, flag):
        self._remove_last = bool(flag)
        self.removeLastChanged.emit(self._remove_last)

    @property
    def remove_last_value(self):
        return self._remove_last_value

    @remove_last_value.setter
    def remove_last_value(self, value):
        self._remove_last_value = value
        self.removeLastValueChanged.emit(self._remove_last_value)

    @property
    def suffix_check(self):
        return self._suffix_check

    @suffix_check.setter
    def suffix_check(self, flag):
        self._suffix_check = bool(flag)
        self.suffixCheckChanged.emit(self._suffix_check)

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, value):
        self._suffix = str(value)
        self.suffixChanged.emit(self._suffix)

    @property
    def selected_prefix(self):
        return self._selected_prefix

    @selected_prefix.setter
    def selected_prefix(self, value):
        self._selected_prefix = int(value)
        self.selectedPrefixChanged.emit(self._selected_prefix)

    @property
    def selected_suffix(self):
        return self._selected_suffix

    @selected_suffix.setter
    def selected_suffix(self, value):
        self._selected_suffix = int(value)
        self.selectedSuffixChanged.emit(self._selected_suffix)

    @property
    def suffixes(self):
        if not self._config:
            return

        suffixes = self._config.get('suffixes', default=list())
        if not suffixes:
            naming_config = tp.ConfigsMgr().get_config('tpDcc-naming')
            if naming_config:
                suffixes = naming_config.get('suffixes', default=dict())

        return suffixes

    @property
    def rename_settings(self):
        prefix = self.prefix if self.prefix_check else ''
        remove_first = self.remove_first_value if self.remove_first else 0
        suffix = self.suffix if self.suffix_check else ''
        remove_last = self.remove_last_value if self.remove_last else 0

        return {
            'prefix': prefix,
            'remove_first': remove_first,
            'suffix': suffix,
            'remove_last': remove_last
        }


class PrefixSuffixWidgetController(object):
    def __init__(self, client, model):
        super(PrefixSuffixWidgetController, self).__init__()

        self._client = client
        self._model = model

    def toggle_prefix_check(self, flag):
        self._model.prefix_check = flag

    def change_prefix(self, new_prefix):
        self._model.prefix = new_prefix

    def toggle_remove_first(self, flag):
        self._model.remove_first = flag

    def change_remove_first_value(self, value):
        self._model.remove_first_value = value

    def toggle_suffix_check(self, flag):
        self._model.suffix_check = flag

    def change_suffix(self, new_suffix):
        self._model.suffix = new_suffix

    def toggle_remove_last(self, flag):
        self._model.remove_last = flag

    def change_remove_last_value(self, value):
        self._model.remove_last_value = value

    def change_selected_prefix(self, index):
        self._model.selected_prefix = index

    def change_selected_suffix(self, index):
        self._model.selected_suffix = index

    @tp.Dcc.get_undo_decorator()
    def add_prefix(self):
        global_data = self._model.global_data
        new_prefix = self._model.prefix
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.add_prefix(
            new_prefix, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_prefix(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_prefix(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_first(self):
        count = self._model.remove_first_value
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_first(
            count=count, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_last(self):
        count = self._model.remove_last_value
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_last(
            count=count, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def add_suffix(self):
        global_data = self._model.global_data
        new_suffix = self._model.suffix
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.add_suffix(
            new_suffix, rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )

    @tp.Dcc.get_undo_decorator()
    def remove_suffix(self):
        global_data = self._model.global_data
        rename_shape = global_data.get('rename_shape', True)
        hierarchy_check = global_data.get('hierarchy_check', False)
        only_selection = global_data.get('only_selection', False)
        filter_type = global_data.get('filter_type', 0)

        return self._client.remove_suffix(
            rename_shape=rename_shape, hierarchy_check=hierarchy_check,
            only_selection=only_selection, filter_type=filter_type
        )


def preffix_suffix_widget(client, config=None, parent=None):
    config = config or tp.ToolsMgr().get_tool_config('tpDcc-tools-renamer')

    model = PrefixSuffixWidgetModel(config=config)
    controller = PrefixSuffixWidgetController(client=client, model=model)
    view = PrefixSuffixView(model=model, controller=controller, parent=parent)

    return view
