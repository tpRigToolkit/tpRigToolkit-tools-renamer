#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains manual rename widgets for tpRenamer
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import Signal

from tpDcc import dcc
from tpDcc.managers import resources
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import accordion, dividers, buttons

from tpDcc.tools.renamer.widgets import renamerwidget, replacerwidget, prefixsuffixwidget, numbersidewidget
from tpDcc.tools.renamer.widgets import namespacewidget, utilswidget


class ManualRenameWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    replaceUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(ManualRenameWidget, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(ManualRenameWidget, self).ui()

        manual_accordion = accordion.AccordionWidget(parent=self)
        self.main_layout.addWidget(manual_accordion)

        self._renamer_widget = renamerwidget.renamer_widget(client=self._controller.client, parent=self)
        self._prefix_suffix_widget = prefixsuffixwidget.preffix_suffix_widget(
            client=self._controller.client, naming_config=self._model.naming_config, parent=self)
        self._number_side_widget = numbersidewidget.number_side_widget(client=self._controller.client, parent=self)
        self._namespace_widget = None
        if dcc.client().is_maya():
            self._namespace_widget = namespacewidget.namespace_widget(client=self._controller.client, parent=self)
        self._replacer_widget = replacerwidget.replacer_widget(client=self._controller.client, parent=self)
        self._utils_widget = utilswidget.utils_widget(client=self._controller.client, parent=self)

        manual_accordion.add_item('Name', self._renamer_widget)
        manual_accordion.add_item('Prefix/Suffix', self._prefix_suffix_widget)
        manual_accordion.add_item('Number & Side', self._number_side_widget)
        if self._namespace_widget:
            manual_accordion.add_item('Namespace', self._namespace_widget)
        manual_accordion.add_item('Search & Replace', self._replacer_widget)
        manual_accordion.add_item('Utils', self._utils_widget)

        self._rename_btn = buttons.BaseButton('Rename')
        self._rename_btn.setIcon(resources.icon('rename'))
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._rename_btn)

    def setup_signals(self):
        self._model.globalAttributeChanged.connect(self._on_updated_global_attribute)
        self._rename_btn.clicked.connect(self._on_rename)

    def refresh(self):
        self._update_global_attribute()

    def _update_global_attribute(self):
        global_attributes_dict = {
            'selection_type': self._model.selection_type,
            'filter_type': self._model.filter_type,
            'hierarchy_check': self._model.hierarchy_check,
            'rename_shape': self._model.rename_shape,
            'only_selection': True if self._model.selection_type == 0 else False
        }

        for widget in [self._renamer_widget, self._prefix_suffix_widget, self._number_side_widget,
                       self._namespace_widget, self._replacer_widget, self._utils_widget]:
            if not widget:
                continue
            widget.model.global_data = global_attributes_dict

    def _on_updated_global_attribute(self):
        self._update_global_attribute()

    def _on_rename(self):

        models_data = dict()

        for widget in [self._renamer_widget, self._prefix_suffix_widget, self._number_side_widget,
                       self._namespace_widget, self._replacer_widget]:
            if not widget:
                continue

            renaming_data = widget.model.rename_settings
            models_data.update(renaming_data)

        return self._controller.rename(**models_data)
