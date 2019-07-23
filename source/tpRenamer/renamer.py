#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fully featured renamer tool
"""

from __future__ import print_function, division, absolute_import

import traceback

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpRenamer
import tpQtLib
import tpDccLib as tp
from tpPyUtils import decorators, strings
from tpQtLib.core import window
from tpQtLib.widgets import splitters, search, button
from tpRenamer.core import manualrenamewidget, autorenamewidget

NAMING_IT_AVAILABLE = True
try:
    import tpNameIt
    from tpNameIt.core import nameit
except ImportError:
    NAMING_IT_AVAILABLE = False

if tp.is_maya():
    import tpMayaLib as maya
    from tpMayaLib.core import decorators as maya_decorators
    undo_decorator = maya_decorators.undo
else:
    undo_decorator = decorators.empty_decorator


class Renamer(window.MainWindow, object):
    def __init__(self):

        self._sel_objs = None

        super(Renamer, self).__init__(
            name='RenamerBaseWindow',
            title='Renamer',
            size=(350, 700),
            fixed_size=False,
            auto_run=True,
            frame_less=True,
            use_style=False
        )

    def ui(self):
        super(Renamer, self).ui()

        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignLeft)
        top_layout.setContentsMargins(2, 2, 2, 2)
        top_layout.setSpacing(2)
        buttons_grp = QButtonGroup(self)
        buttons_grp.setExclusive(True)
        self._objects_btn = QPushButton('Objects')
        self._objects_btn.setMinimumWidth(55)
        self._objects_btn.setCheckable(True)
        self._objects_btn.setChecked(True)
        self._materials_btn = QPushButton('Materials')
        self._materials_btn.setMinimumWidth(55)
        self._materials_btn.setCheckable(True)
        self._layers_btn = QPushButton('Layers')
        self._layers_btn.setMinimumWidth(55)
        self._layers_btn.setCheckable(True)
        self._cameras_btn = QPushButton('Cameras')
        self._cameras_btn.setMinimumWidth(55)
        self._cameras_btn.setCheckable(True)
        self._lights_btn = QPushButton('Lights')
        self._lights_btn.setMinimumWidth(55)
        self._lights_btn.setCheckable(True)
        self._files_btn = QPushButton('Files')
        self._files_btn.setMinimumWidth(55)
        self._files_btn.setCheckable(True)
        self.main_layout.addLayout(top_layout)
        self.main_layout.addLayout(splitters.SplitterLayout())
        buttons_grp.addButton(self._objects_btn)
        buttons_grp.addButton(self._materials_btn)
        buttons_grp.addButton(self._layers_btn)
        buttons_grp.addButton(self._cameras_btn)
        buttons_grp.addButton(self._lights_btn)
        buttons_grp.addButton(self._files_btn)
        top_layout.addWidget(self._objects_btn)
        top_layout.addWidget(self._materials_btn)
        top_layout.addWidget(self._layers_btn)
        top_layout.addWidget(self._cameras_btn)
        top_layout.addWidget(self._lights_btn)
        top_layout.addWidget(self._files_btn)

        top_layout.addWidget(splitters.get_horizontal_separator_widget())
        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(4, 0, 4, 0)
        selection_layout.setSpacing(2)
        top_layout.addLayout(selection_layout)

        selection_mode_lbl = QLabel('Selection: ')
        self._all_radio = QRadioButton('All')
        self._all_radio.setFixedHeight(19)
        self._all_radio.setChecked(True)
        self._all_radio.setAutoExclusive(True)
        self._selected_radio = QRadioButton('Selected')
        self._selected_radio.setFixedHeight(19)
        self._selected_radio.setAutoExclusive(True)
        self._hierarchy_cbx = QCheckBox('Hierarchy')
        self._hierarchy_cbx.setFixedHeight(19)

        selection_layout.addWidget(selection_mode_lbl)
        selection_layout.addWidget(self._all_radio)
        selection_layout.addWidget(self._selected_radio)
        selection_layout.addWidget(self._hierarchy_cbx)

        self._splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self._splitter)

        self.rename_tab = QTabWidget()
        self._splitter.addWidget(self.rename_tab)

        self.manual_rename_widget = manualrenamewidget.ManualRenameWidget()
        self.auto_rename_widget = autorenamewidget.AutoRenameWidget()

        self.rename_tab.addTab(self.manual_rename_widget, 'Manual')
        if NAMING_IT_AVAILABLE:
            self.rename_tab.addTab(self.auto_rename_widget, 'Auto')

        names_widget = QWidget()
        names_layout = QVBoxLayout()
        names_layout.setContentsMargins(0, 0, 0, 0)
        names_layout.setSpacing(2)
        names_widget.setLayout(names_layout)
        self._splitter.addWidget(names_widget)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(10, 0, 10, 0)
        filter_layout.setSpacing(2)
        names_layout.addLayout(filter_layout)
        refresh_icon = tpQtLib.resource.icon('refresh')
        self._refresh_names_btn = button.IconButton(icon=refresh_icon, icon_padding=2, button_style=button.ButtonStyles.FlatStyle)
        self._names_filter = search.SearchFindWidget()
        self._search_lbl = QLabel('0 found')
        filter_layout.addWidget(self._refresh_names_btn)
        filter_layout.addWidget(self._names_filter)
        filter_layout.addWidget(self._search_lbl)

        types_layout = QHBoxLayout()
        types_layout.setContentsMargins(0, 0, 0, 0)
        types_layout.setSpacing(2)
        names_layout.addLayout(types_layout)

        self._transforms_btn = None
        self._shapes_btn = None
        self._cameras_btn = None
        self._layers_btn = None
        if tp.is_maya():
            self._transforms_btn = QPushButton('Transforms')
            self._transforms_btn.setCheckable(True)
            self._transforms_btn.setChecked(True)
            self._shapes_btn = QPushButton('Shapes')
            self._shapes_btn.setCheckable(True)
            types_layout.addWidget(self._transforms_btn)
            types_layout.addWidget(self._shapes_btn)

        self._names_list = QTreeWidget(self)
        self._names_list.setHeaderHidden(True)
        self._names_list.setSortingEnabled(False)
        self._names_list.setRootIsDecorated(False)
        self._names_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._names_list.sortByColumn(0, Qt.AscendingOrder)
        self._names_list.setUniformRowHeights(True)
        self._names_list.setAlternatingRowColors(True)

        names_layout.addWidget(self._names_list)

        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.setAlignment(Qt.AlignLeft)
        bottom_buttons_layout.setContentsMargins(2, 2, 2, 2)
        bottom_buttons_layout.setSpacing(2)
        names_layout.addLayout(bottom_buttons_layout)

        preview_icon = tpQtLib.resource.icon('preview')
        self._sort_btn = QPushButton('Sort')
        self._sort_btn.setMinimumWidth(40)
        self._all_btn = QPushButton('All')
        self._all_btn.setMinimumWidth(40)
        self._none_btn = QPushButton('None')
        self._none_btn.setMinimumWidth(40)
        bottom_buttons_layout.addWidget(self._sort_btn)
        bottom_buttons_layout.addWidget(self._all_btn)
        bottom_buttons_layout.addWidget(self._none_btn)

        self._hide_default_scene_nodes_cbx = None
        if tp.is_maya():
            bottom_buttons_layout.addWidget(splitters.get_horizontal_separator_widget())
            self._hide_default_scene_nodes_cbx = QCheckBox('Hide Default Scene Objects')
            self._hide_default_scene_nodes_cbx.setChecked(True)
            bottom_buttons_layout.addWidget(self._hide_default_scene_nodes_cbx)

        names_layout.addLayout(splitters.SplitterLayout())

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(2)
        names_layout.addLayout(preview_layout)

        self._preview_btn = QPushButton('Preview')
        self._preview_btn.setIcon(preview_icon)
        self._preview_btn.setCheckable(True)
        self._preview_btn.setChecked(True)
        self._preview_btn.setMinimumWidth(100)
        self._preview_btn.setMaximumWidth(100)
        self._rename_btn = QPushButton('Select objects in the list to rename ...')
        self._rename_btn.setEnabled(False)
        preview_layout.addWidget(self._preview_btn)
        preview_layout.addWidget(self._rename_btn)

        self.update_names_list()

    def setup_signals(self):

        self.rename_tab.currentChanged.connect(self._on_tab_changed)
        self._refresh_names_btn.clicked.connect(self.update_names_list)

        self._all_radio.clicked.connect(self.update_names_list)
        self._selected_radio.clicked.connect(self.update_names_list)
        self._hierarchy_cbx.toggled.connect(self.update_names_list)

        self._names_filter.textChanged.connect(self._on_filter_names_list)

        if self._hide_default_scene_nodes_cbx:
            self._hide_default_scene_nodes_cbx.toggled.connect(self.update_names_list)
        if self._transforms_btn:
            self._transforms_btn.toggled.connect(self.update_names_list)
        if self._shapes_btn:
            self._shapes_btn.toggled.connect(self.update_names_list)
        if self._cameras_btn:
            self._cameras_btn.toggled.connect(self.update_names_list)

        self._names_list.itemSelectionChanged.connect(self._on_item_selection_changed)

        self._none_btn.clicked.connect(self._on_select_none_clicked)
        self._all_btn.clicked.connect(self._on_select_all_clicked)

        self.manual_rename_widget.renameUpdate.connect(self.update_current_items)
        self.manual_rename_widget.replaceUpdate.connect(self.update_current_items)

        self._preview_btn.toggled.connect(self.update_current_items)
        self._rename_btn.clicked.connect(self._on_rename)

    #
    #     self._prefix_check.stateChanged.connect(self._prefix_line.setEnabled)
    #     self._suffix_check.stateChanged.connect(self._suffix_line.setEnabled)
    #     self._prefix_check.stateChanged.connect(self._update_example_rename)
    #     self._suffix_check.stateChanged.connect(self._update_example_rename)
    #
    #     self._renamer_mult_method_combo.currentIndexChanged.connect(self._toggle_mult_naming_method)
    #
    #     self._lower_radio.clicked.connect(self._update_example_rename)
    #     self._upper_radio.clicked.connect(self._update_example_rename)
    #     self._frame_pad_spin.valueChanged.connect(self._update_example_rename)
    #
    #     self._none_side.toggled.connect(self._update_example_rename)
    #     self._right_side.toggled.connect(self._update_example_rename)
    #     self._center_side.toggled.connect(self._update_example_rename)
    #     self._mid_side.toggled.connect(self._update_example_rename)
    #     self._left_side.toggled.connect(self._update_example_rename)
    #     self._capital_side.toggled.connect(self._update_example_rename)
    #
    #     self._renamer_line.textChanged.connect(self._update_example_rename)
    #     self._prefix_line.textChanged.connect(self._update_example_rename)
    #     self._suffix_line.textChanged.connect(self._update_example_rename)
    #
    #     self._selected_radio.toggled.connect(self._update_hierarchy_cbx)
    #     self._all_radio.toggled.connect(self._update_hierarchy_cbx)
    #
    #     self._add_prefix_btn.clicked.connect(self.add_prefix)
    #     self._add_suffix_btn.clicked.connect(self.add_suffix)
    #     self._select_hierarchy_btn.clicked.connect(self.select_hierarchy)
    #
    #     self._renamer_btn.clicked.connect(self.rename_nodes)
    #     self._replace_btn.clicked.connect(self.replace_nodes)
    #
    #     self.edit_btn.clicked.connect(self._on_open_naming_manager)
    #     self.rules_list.itemSelectionChanged.connect(self._on_change_name_rule)

        # self._update_example_rename()

    def keyPressEvent(self, event):

        # Prevent lost focus when writing on QLineEdits
        if event.key() in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_CapsLock):
            event.accept()
        else:
            event.ignore()

    def update_names_list(self):
        """
        Function that updates names list taking into account current nomenclature type
        """

        self._names_list.clear()
        self._names_list.setSortingEnabled(True)

        try:
            objs_names = list()
            if self._all_radio.isChecked():
                objs_names.extend(tp.Dcc.all_scene_objects(full_path=True))
            elif self._selected_radio.isChecked():
                objs_names.extend(tp.Dcc.selected_nodes(full_path=True))
                if objs_names and self._hierarchy_cbx.isChecked():
                    children_list = list()
                    for obj in objs_names:
                        children = tp.Dcc.list_children(obj, all_hierarchy=True, full_path=True)
                        if children:
                            children_list.extend(children)
                    children_list = list(set(children_list))
                    objs_names.extend(children_list)

            if self._objects_btn.isChecked():
                self._update_objects_names_list(objs_names)

            self._on_filter_names_list(self._names_filter.get_text())
        finally:
            self._names_list.setSortingEnabled(False)

    def update_current_items(self):
        """
        Function that updates the names of the current selected items
        """

        self._update_current_objects_items()

    def _update_objects_names_list(self, nodes):
        """
        Internal function that updates name list with current scene objects
        """

        discard_nodes = list()
        if tp.is_maya():
            discard_nodes.extend(['persp', 'top', 'front', 'side'])
            types_to_discard = ['displayLayer', 'renderLayer', 'displayLayerManager',
                                'renderLayerManager', 'shapeEditorManager', 'poseInterpolatorManager', 'lightLinker']
            for node_type in types_to_discard:
                discard_nodes.extend(tp.Dcc.list_nodes(node_type=node_type))

        discard_nodes.extend(tp.Dcc.list_nodes(node_type='camera'))

        if self._hide_default_scene_nodes_cbx and self._hide_default_scene_nodes_cbx.isChecked():
            discard_nodes.extend(tp.Dcc.default_scene_nodes(full_path=False))
        if self._transforms_btn and not self._transforms_btn.isChecked():
            discard_nodes.extend(tp.Dcc.list_nodes(node_type='transform'))
        if self._shapes_btn:
            if not self._shapes_btn.isChecked():
                discard_nodes.extend(tp.Dcc.all_shapes_nodes(full_path=True))
            else:
                shape_nodes = list()
                for obj in nodes:
                    shapes = tp.Dcc.list_shapes(obj, full_path=True)
                    if shapes:
                        shape_nodes.extend(shapes)
                nodes.extend(shape_nodes)

        nodes = list(set(nodes))

        for obj in nodes:
            if obj in discard_nodes:
                continue
            node_name = tp.Dcc.node_short_name(obj)
            item = QTreeWidgetItem(self._names_list, [node_name])
            item.obj = node_name
            item.preview_name = ''
            item.full_name = obj
            if tp.is_maya():
                mobj = maya.OpenMaya.MObject()
                sel = maya.OpenMaya.MSelectionList()
                sel.add(obj)
                sel.getDependNode(0, mobj)
                item.handle = maya.OpenMaya.MObjectHandle(mobj)

            self._names_list.addTopLevelItem(item)

    def _update_current_objects_items(self):
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            item.preview_name = ''
            if hasattr(item, 'obj'):
                item.setText(0, item.obj)

        if self._preview_btn.isChecked():
            selected_items = self._names_list.selectedItems()
            self._set_preview_names(items=selected_items)

    def _find_available_name(self, name, prefix=None, suffix=None, side='',  index=-1, padding=0, letters=False, capital=False, remove_first=0, remove_last=0, find_str=None, replace_str=None, joint_end=False):
        """
        Recursively find a free name matching specified criteria
        @param name: str, Name to check if already exists in the scene
        @param suffix: str, Suffix for the name
        @param index: int, Index of the name
        @param padding: int, Padding for the characters/numbers
        @param letters: bool, True if we want to use letters when renaming multiple nodes
        @param capital: bool, True if we want letters to be capital
        """

        if prefix:
            if side and side != '':
                test_name = '{}_{}_{}'.format(prefix, side, name)
            else:
                test_name = '{}_{}'.format(prefix, name)
        else:
            if side and side != '':
                test_name = '{}_{}'.format(side, name)
            else:
                test_name = name

        if index >= 0:
            if letters is True:
                letter = strings.get_alpha(index, capital)
                test_name = '{}_{}'.format(test_name, letter)
            else:
                test_name = '{}_{}'.format(test_name, str(index).zfill(padding+1))

        if suffix:
            test_name = '{}_{}'.format(test_name, suffix)

        if remove_first and remove_first > 0:
            test_name = test_name[remove_first:]

        if remove_last and remove_last > 0:
            test_name = test_name[:-remove_last]

        if find_str != None and find_str != '' and replace_str != None:
            test_name = test_name.replace(find_str, replace_str)

        selected_items = self._names_list.selectedItems()
        item_names = [item.obj for item in selected_items]

        # if object exists, try next index
        if tp.Dcc.object_exists(test_name) or test_name in item_names:
            new_index = int(index) + 1
            return self._find_available_name(
                name, prefix=prefix, index=new_index, padding=padding,
                letters=letters, capital=capital, remove_first=remove_first, remove_last=remove_last,
                joint_end=joint_end, find_str=find_str, replace_str=replace_str
            )

        return test_name

    def _generate_preview_names(self, items):

        text, prefix, suffix, padding, naming_method, upper, side, remove_first, remove_last, joint_end = self.manual_rename_widget.get_rename_settings()
        find_str, replace_str = self.manual_rename_widget.get_replace_settings()

        duplicated_names = dict()
        generated_names = list()

        for item in items:
            if not text:
                base_name = item.obj
            else:
                base_name = text

            if base_name == item.obj and not prefix and not suffix and not side:
                generate_preview_name = False
            else:
                generate_preview_name = True
            if base_name in duplicated_names:
                duplicated_names[base_name] += 1
            else:
                duplicated_names[base_name] = 0

            print('Generating preview name: {}'.format(generate_preview_name))

            if generate_preview_name:

                if base_name == item.obj and (prefix or suffix or side):
                    index = None
                else:
                    index = duplicated_names[base_name]

                preview_name = self._find_available_name(base_name, prefix=prefix, side=side, suffix=suffix,
                                                         index=index, padding=padding,
                                                         letters=naming_method, capital=upper, joint_end=joint_end,
                                                         remove_first=remove_first, remove_last=remove_last,
                                                         find_str=find_str, replace_str=replace_str)

                while preview_name in generated_names:
                    duplicated_names[base_name] += 1
                    preview_name = self._find_available_name(base_name, prefix=prefix, side=side, suffix=suffix,
                                              index=duplicated_names[base_name], padding=padding,
                                              letters=naming_method, capital=upper, joint_end=joint_end,
                                              remove_first=remove_first, remove_last=remove_last,
                                              find_str=find_str, replace_str=replace_str)
            else:
                preview_name = base_name

            item.preview_name = preview_name
            generated_names.append(preview_name)

    def _set_preview_names(self, items):
        """
        Internal function that sets the preview name for the given items
        :param items:
        :return:
        """

        self._generate_preview_names(items)

        if self._preview_btn.isChecked():
            for item in items:
                if item.preview_name:
                    item.setText(0, item.preview_name)

    def _on_filter_names_list(self, filter_text):
        """
        This function is called each time the user enters text in the search line widget
        Shows or hides elements in the list taking in account the filter_text
        :param filter_text: str, current text
        """

        nodes_found = 0
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            # item.setHidden(filter_text not in item.text(0))
            if filter_text not in item.text(0):
                item.setHidden(True)
            else:
                item.setHidden(False)
                nodes_found += 1

        if filter_text:
            self._search_lbl.setText('{} found'.format(nodes_found))
        else:
            self._search_lbl.setText('0 found')

    def _on_item_selection_changed(self):
        """
        Internal callback function that is triggered when the user selects an item in the names list
        """

        selected_items = self._names_list.selectedItems()
        item_names = [item.obj for item in selected_items]
        if len(selected_items) > 0:
            self._rename_btn.setText('Rename')
            self._rename_btn.setEnabled(True)
        else:
            self._rename_btn.setText('Select objects in the list to rename ...')
            self._rename_btn.setEnabled(False)

        # We reset name to original value
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            if item.text(0) in item_names:
                continue
            if hasattr(item, 'obj'):
                item.setText(0, item.obj)

        self._set_preview_names(items=selected_items)

    def _on_select_all_clicked(self):
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            item.setSelected(True)

    def _on_select_none_clicked(self):
        for i in range(self._names_list.topLevelItemCount()):
            item = self._names_list.topLevelItem(i)
            item.setSelected(False)

    def _on_tab_changed(self, tab_index):

        if tab_index != 1 or not NAMING_IT_AVAILABLE:
            return

        self.auto_rename_widget.update_rules()

    @undo_decorator
    def _on_rename(self):
        items_to_rename = self._names_list.selectedItems()
        for item in items_to_rename:
            try:
                if hasattr(item, 'handle'):
                    if tp.is_maya():
                        mobj = item.handle.object()
                        dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
                        full_name = dag_path.fullPathName()
                        tp.Dcc.rename_node(full_name, item.preview_name)
                        item.obj = item.preview_name
                        item.preview_name = ''
                else:
                    tp.Dcc.rename_node(item.full_name, item.preview_name)
                    item.obj = item.preview_name
                    item.preview_name = ''
            except Exception as e:
                tpRenamer.logger.warning('Impossible to rename: {} to {}'.format(item.full_name, item.preview_name))
                tpRenamer.logger.error('{} | {}'.format(e, traceback.format_exc()))

        self.update_current_items()
        self._names_list.clearSelection()


def run():
    win = Renamer()
    win.show()
    return win
