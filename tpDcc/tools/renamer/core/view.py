#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renamer widget view class implementation
"""

from __future__ import print_function, division, absolute_import

import logging

from Qt.QtCore import Qt
from Qt.QtWidgets import QSizePolicy, QButtonGroup, QSpacerItem

from tpDcc import dcc
from tpDcc.managers import resources
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, dividers, splitter, buttons, combobox, checkbox, tabs, stack

from tpDcc.tools.renamer.widgets import manualrenamewidget, autorenamewidget, categorywidget

LOGGER = logging.getLogger('tpDcc-tools-renamer')


class RenamerView(base.BaseWidget, object):
    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(RenamerView, self).__init__(parent=parent)

        self.refresh()

    @property
    def model(self):
        return self._model

    @property
    def controller(self):
        return self._controller

    def ui(self):
        super(RenamerView, self).ui()

        top_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        top_layout.setAlignment(Qt.AlignLeft)
        self._buttons_grp = QButtonGroup(self)
        self._buttons_grp.setExclusive(True)
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(dividers.DividerLayout())

        self._categories_layout = layouts.HorizontalLayout(spacing=2, margins=(2, 2, 2, 2))
        self._categories_layout.setAlignment(Qt.AlignLeft)

        selection_layout = layouts.HorizontalLayout(spacing=2, margins=(4, 0, 4, 0))
        top_layout.addLayout(selection_layout)

        self._all_radio = buttons.BaseRadioButton('All', parent=self)
        self._all_radio.setFixedHeight(19)
        self._all_radio.setAutoExclusive(True)
        self._selected_radio = buttons.BaseRadioButton('Selected', parent=self)
        self._selected_radio.setFixedHeight(19)
        self._selected_radio.setChecked(True)
        self._selected_radio.setAutoExclusive(True)
        self._hierarchy_cbx = checkbox.BaseCheckBox('Hierarchy', parent=self)
        self._hierarchy_cbx.setFixedHeight(19)
        self._node_types_combo = combobox.BaseComboBox(parent=self)
        self._auto_rename_shapes_cbx = None
        self._auto_rename_shapes_cbx = checkbox.BaseCheckBox('Auto Rename Shapes', parent=self)
        self._auto_rename_shapes_cbx.setChecked(True)
        if not dcc.client().is_maya():
            self._auto_rename_shapes_cbx.setVisible(False)

        selection_layout.addWidget(self._selected_radio)
        selection_layout.addWidget(self._all_radio)
        selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        selection_layout.addWidget(self._hierarchy_cbx)
        selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        selection_layout.addWidget(self._node_types_combo)
        if self._auto_rename_shapes_cbx:
            selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
            selection_layout.addWidget(self._auto_rename_shapes_cbx)

        self._splitter = splitter.CollapsibleSplitter(parent=self)
        self._splitter.setOrientation(Qt.Horizontal)
        self._splitter.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self._splitter.setMinimumHeight(750)
        self.main_layout.addWidget(self._splitter)

        self._rename_tab = tabs.BaseTabWidget(parent=self)
        self._splitter.addWidget(self._rename_tab)

        self._manual_rename_widget = manualrenamewidget.ManualRenameWidget(
            model=self._model, controller=self._controller, parent=self)
        self._auto_rename_widget = autorenamewidget.AutoRenameWidget(
            model=self._model, controller=self._controller, parent=self)

        self._rename_tab.addTab(self._manual_rename_widget, 'Manual')
        self._rename_tab.addTab(self._auto_rename_widget, 'Auto')

        self._stack = stack.SlidingStackedWidget()
        # splitter_right_widget = QWidget()
        # splitter_right_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        # splitter_right_layout.addLayout(self._categories_layout)
        # splitter_right_layout.addWidget(self._stack)
        # splitter_right_widget.setLayout(splitter_right_layout)
        # self._splitter.addWidget(splitter_right_widget)
        #
        # no_items_widget = QFrame()
        # no_items_widget.setFrameShape(QFrame.StyledPanel)
        # no_items_widget.setFrameShadow(QFrame.Sunken)
        # no_items_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        # no_items_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        # no_items_widget.setLayout(no_items_layout)
        # no_items_lbl = label.BaseLabel()
        # no_items_pixmap = tp.ResourcesMgr().pixmap('no_items')
        # no_items_lbl.setPixmap(no_items_pixmap)
        # no_items_lbl.setAlignment(Qt.AlignCenter)
        # no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        # no_items_layout.addWidget(no_items_lbl)
        # no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        #
        # self._stack.addWidget(no_items_widget)

        self._splitter.handle(0).collapse()
        self._splitter.setSizes([1, 0])

    def setup_signals(self):
        self._stack.animFinished.connect(self._on_stack_anim_finished)
        self._rename_tab.currentChanged.connect(self._on_tab_changed)
        self._selected_radio.clicked.connect(self._controller.set_selected)
        self._all_radio.clicked.connect(self._controller.set_all_selection)
        self._hierarchy_cbx.toggled.connect(self._controller.hierarchy_check_toggle)
        self._node_types_combo.currentIndexChanged.connect(self._controller.set_filter_type)
        self._auto_rename_shapes_cbx.toggled.connect(self._controller.auto_rename_shapes_check_toggle)

        self._model.hierarchyCheckChanged.connect(self._on_toggle_hierarchy_cbx)
        self._model.renameShapeChanged.connect(self._on_toggle_auto_rename_shape_cbx)
        self._model.filterTypeChanged.connect(self._on_filter_type_changed)

    def refresh(self):
        """
        Syncs view to the current state of its model
        """

        self._hierarchy_cbx.setChecked(self._model.hierarchy_check)

        self._node_types_combo.clear()
        for btn in self._buttons_grp.buttons():
            self._buttons_grp.removeButton(btn)

        node_types = self._model.node_types
        if not node_types:
            self._node_types_combo.setVisible(False)
        else:
            self._node_types_combo.setVisible(True)
            for node_type in node_types:
                self._node_types_combo.addItem(str(node_type).split('.')[-1])

        categories = self._model.categories or dict()
        nodes_to_discard = self._model.nodes_to_discard
        types_to_discard = self._model.types_to_discard
        for node_type in types_to_discard:
            nodes_to_discard.extend(dcc.client().list_nodes(node_type=node_type))

        for i, category in enumerate(categories):
            for category_name, category_data in category.items():
                title = category_data.get('title', category)
                icon = category_data.get('icon', None)
                types = category_data.get('types', dict())
                category_btn = buttons.BaseButton(title)
                category_btn.setCheckable(True)
                if icon:
                    category_btn.setIcon(resources.icon(icon))
                if i == 0:
                    category_btn.setChecked(True)
                self._buttons_grp.addButton(category_btn)
                self._categories_layout.addWidget(category_btn)
                category_widget = categorywidget.CategoryWidget(types=types, nodes_to_discard=nodes_to_discard)
                self._stack.addWidget(category_widget)

                # category_widget.doRefresh.connect(self._on_refresh_category)
                # category_widget.doPreview.connect(self._set_preview_names)
                # category_widget.togglePreview.connect(self.update_current_items)
                # category_widget.doRename.connect(self._on_rename)
                # category_btn.clicked.connect(partial(self._on_category_selected, i + 1))

        self._auto_rename_widget.refresh()

        self._controller.update_rules()

    def _on_stack_anim_finished(self, index):
        """
        Internal callback function that is called when stack animation is completed
        :param index:
        :return:
        """

        for btn in self._buttons_grp.buttons():
            btn.setEnabled(True)
        category_widget = self._stack.current_widget
        if not category_widget:
            return
        # self._on_refresh_category(category_widget)

    def _on_tab_changed(self, tab_index):
        """
        Internal callback function that is called when tab widget is changed by the user
        :param tab_index: int
        """

        if tab_index != 1:
            return

        self._controller.update_rules()

    def _on_toggle_hierarchy_cbx(self, flag):
        """
        Internal callback function called when the user toggles hierarchy check box
        :param flag: bool
        """

        self._hierarchy_cbx.setChecked(flag)

    def _on_toggle_auto_rename_shape_cbx(self, flag):
        """
        Internal callback function called when the user toggles auto rename shape check box
        :param flag: bool
        """

        self._auto_rename_shapes_cbx.setChecked(flag)

    def _on_filter_type_changed(self, value):
        """
        Internal callback function that is called when user changes the filter type combo box
        :param value: str
        """

        self._node_types_combo.setCurrentText(value)
