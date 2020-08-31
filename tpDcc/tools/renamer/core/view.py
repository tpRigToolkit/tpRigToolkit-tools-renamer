#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renamer widget view class implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, dividers, splitter, buttons, combobox, checkbox, tabs, stack
from tpDcc.libs.qt.widgets import accordion

from tpDcc.tools.renamer.widgets import renamerwidget, prefixsuffixwidget, categorywidget, numbersidewidget
from tpDcc.tools.renamer.widgets import namespacewidget, replacerwidget, utilswidget

logger = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


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
        if not tp.is_maya():
            self._auto_rename_shapes_cbx.setVisible(False)
            self._auto_rename_shapes_cbx.setEnabled(False)

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

        self._manual_rename_widget = ManualRenameWidget(model=self._model, controller=self._controller, parent=self)
        # self._auto_rename_widget = AutoRenameWidget(parent=self)
        # # self.auto_rename_widget = AutoRenameWidget(naming_lib=self._name_lib)

        self._rename_tab.addTab(self._manual_rename_widget, 'Manual')
        # self._rename_tab.addTab(self._auto_rename_widget, 'Auto')

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

        # self._manual_rename_widget.doName.connect(self._controller.rename_simple)
        # self._manual_rename_widget.doAddPrefix.connect(self._controller.add_prefix)
        # self._manual_rename_widget.doRemovePrefix.connect(self._controller.remove_prefix)
        # self._manual_rename_widget.doRemoveFirst.connect(self._controller.remove_first)

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
                self._node_types_combo.addItem(node_type)

        categories = self._model.categories or dict()
        nodes_to_discard = self._model.nodes_to_discard
        types_to_discard = self._model.types_to_discard
        for node_type in types_to_discard:
            nodes_to_discard.extend(tp.Dcc.list_nodes(node_type=node_type))

        for i, category in enumerate(categories):
            for category_name, category_data in category.items():
                title = category_data.get('title', category)
                icon = category_data.get('icon', None)
                types = category_data.get('types', dict())
                category_btn = buttons.BaseButton(title)
                category_btn.setCheckable(True)
                if icon:
                    category_btn.setIcon(tp.ResourcesMgr().icon(icon))
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

        self._auto_rename_widget.update_rules()

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

        self._hierarchy_cbx.setChecked(flag)

    def _on_filter_type_changed(self, value):
        """
        Internal callback function that is called when user changes the filter type combo box
        :param value: str
        """

        self._node_types_combo.setCurrentText(value)


class ManualRenameWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    replaceUpdate = Signal()

    def __init__(self, model, controller, parent=None):

        self._model = model
        self._controller = controller

        super(ManualRenameWidget, self).__init__(parent=parent)

    def ui(self):
        super(ManualRenameWidget, self).ui()

        manual_accordion = accordion.AccordionWidget()
        self.main_layout.addWidget(manual_accordion)

        self._renamer_widget = renamerwidget.renamer_widget(client=self._controller.client, parent=self)
        self._prefix_suffix_widget = prefixsuffixwidget.preffix_suffix_widget(
            client=self._controller.client, config=self._model.config, parent=self)
        self._number_side_widget = numbersidewidget.number_side_widget(client=self._controller.client, parent=self)
        self._namespace_widget = None
        if tp.is_maya():
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
        self._rename_btn.setIcon(tp.ResourcesMgr().icon('rename'))
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._rename_btn)

    def setup_signals(self):
        self._model.globalAttributeChanged.connect(self._on_updated_global_attribute)
        self._rename_btn.clicked.connect(self._on_rename)

    def _on_updated_global_attribute(self):

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

    def _on_rename(self):

        models_data = dict()

        for widget in [self._renamer_widget, self._prefix_suffix_widget, self._number_side_widget,
                       self._namespace_widget, self._replacer_widget]:
            if not widget:
                continue

            renaming_data = widget.model.rename_settings
            models_data.update(renaming_data)

        return self._controller.rename(**models_data)


class AutoRenameWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(AutoRenameWidget, self).__init__(parent=parent)

    def ui(self):
        super(AutoRenameWidget, self).ui()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        auto_widget = QWidget()
        auto_layout = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        auto_widget.setLayout(auto_layout)
        main_splitter.addWidget(auto_widget)

        self._rules_list = QTreeWidget(self)
        self._rules_list.setHeaderHidden(True)
        self._rules_list.setSortingEnabled(True)
        self._rules_list.setRootIsDecorated(False)
        self._rules_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._rules_list.sortByColumn(0, Qt.AscendingOrder)
        self._rules_list.setUniformRowHeights(True)
        self._rules_list.setAlternatingRowColors(True)

        auto_layout.addWidget(self._rules_list)

        auto_w = QWidget()
        self.auto_l = layouts.VerticalLayout(spacing=0, margins=(0, 0, 0, 0))
        auto_w.setLayout(self.auto_l)
        auto_w.setMinimumWidth(200)
        main_splitter.addWidget(auto_w)

        self.main_auto_layout = QFormLayout()
        self.auto_l.addLayout(self.main_auto_layout)

        self._rename_btn = buttons.BaseButton('Rename')
        self._rename_btn.setIcon(tp.ResourcesMgr().icon('rename'))
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._rename_btn)
