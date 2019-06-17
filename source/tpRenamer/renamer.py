#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fully featured renamer tool
"""

from __future__ import print_function, division, absolute_import

import traceback
from collections import OrderedDict

from tpQtLib.Qt.QtCore import *
from tpQtLib.Qt.QtWidgets import *

import tpRenamer
import tpQtLib
import tpDccLib as tp
from tpPyUtils import decorators
from tpQtLib.core import window, qtutils
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
    from tpMayaLib.core import decorators as maya_decorators, name as naming
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
        self._names_list.setSortingEnabled(True)
        self._names_list.setRootIsDecorated(False)
        self._names_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._names_list.sortByColumn(0, Qt.AscendingOrder)
        self._names_list.setUniformRowHeights(True)
        self._names_list.setAlternatingRowColors(True)
        self._names_list.setStyleSheet(
            '''
            QTreeView{alternate-background-color: #3b3b3b;}
            QTreeView::item {padding:3px;}
            QTreeView::item:!selected:hover {
                background-color: #5b5b5b;
                margin-left:-3px;
                border-left:0px;
            }
            QTreeView::item:selected {
                background-color: #48546a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            QTreeView::item:selected:hover {
                background-color: #586c7a;
                border-left:2px solid #6f93cf;
                padding-left:2px;
            }
            '''
        )

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
        self.rename_btn = QPushButton('Rename')
        preview_layout.addWidget(self._preview_btn)
        preview_layout.addWidget(self.rename_btn)

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

    def rename_nodes(self):
        """
        Method that renames selected nodes
        """

        selected_objs = tp.Dcc.selected_nodes(full_path=False)
        rename(selected_objs, *self._get_rename_settings())

    def auto_rename_nodes(self, auto_name):
        """
        Method that auto rename selected nodes
        """

        selected_objs = tp.Dcc.selected_nodes(full_path=False)
        rename(selected_objs, text=auto_name, auto_rename=True)

    def replace_nodes(self):
        """
        Method that replace node names
        """

        replace_text = str(self._replace_line.text())
        with_text = str(self._with_line.text())

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            if self._all_radio.isChecked():
                nodes = maya.cmds.ls()
                replace_nodes = replace(nodes, replace_text, with_text)
            else:
                nodes = maya.cmds.ls(sl=True)

                if self._hierarchy_cbx.isChecked() and self._hierarchy_cbx.isEnabled():
                    new_nodes = list()
                    replace_nodes = list()

                    # First, replace the hierarchy elements of the selected objects
                    for node in nodes:
                        maya.cmds.select(node)
                        maya.cmds.select(hi=True)
                        childs = maya.cmds.ls(sl=True, type='transform')
                        if node in childs:
                            childs.remove(node)
                        for child in childs:
                            new_nodes.append(child)
                        return_nodes = replace(new_nodes, replace_text, with_text)
                        for n in return_nodes:
                            replace_nodes.append(n)

                    # Finally we replace the names of the selected nodes
                    return_nodes = replace(nodes, replace_text, with_text)
                    for n in return_nodes:
                        replace_nodes.append(n)
                else:
                    replace_nodes = replace(nodes, replace_text, with_text)

            try:
                if len(replace_nodes) > 0:
                    maya.cmds.select(replace_nodes)
                    tpRenamer.logger.debug('Successfully renamed ' + str(len(replace_nodes)) + ' node(s)!')
            except:
                maya.cmds.select(clear=True)
        else:
            raise NotImplementedError()

    def update_names_list(self):
        """
        Function that updates names list taking into account current nomenclature type
        """

        self._names_list.clear()

        objs_names = list()
        if self._all_radio.isChecked():
            objs_names.extend(tp.Dcc.all_scene_objects(full_path=False))
        elif self._selected_radio.isChecked():
            objs_names.extend(tp.Dcc.selected_nodes(full_path=False))
            if objs_names and self._hierarchy_cbx.isChecked():
                children_list = list()
                for obj in objs_names:
                    children = tp.Dcc.list_children(obj, all_hierarchy=True, full_path=False)
                    if children:
                        children_list.extend(children)
                children_list = list(set(children_list))
                objs_names.extend(children_list)

        if self._objects_btn.isChecked():
            self._update_objects_names_list(objs_names)
        elif self._materials_btn.isChecked():
            self._update_materials_names_list(objs_names)
        elif self._layers_btn.isChecked():
            self._update_layers_names_list(objs_names)
        elif self._lights_btn.isChecked():
            self._update_assets_names_list(objs_names)
        elif self._files_btn.isChecked():
            self._update_files_names_list(objs_names)

        self._on_filter_names_list(self._names_filter.get_text())

    @undo_decorator
    def add_prefix(self):
        """
        Method that adds a prefix to selected nodes
        """

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            sel = maya.cmds.ls(sl=True)
        else:
            raise NotImplementedError()

        prefix = str(self._add_prefix_line.text())
        if len(sel) > 0:
            if prefix == '':
                pass
            else:
                for obj in sel:
                    new_name = '%s_%s' % (prefix, obj)
                    maya.cmds.rename(obj, new_name)
                    tpRenamer.logger.debug('Sucesfully renamed ' + str(len(sel)) + ' node(s)!')

    @undo_decorator
    def add_suffix(self):
        """
        Method that adds a suffix to selected nodes
        """

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            sel = maya.cmds.ls(selection=True)
        else:
            raise NotImplementedError()

        suffix = str(self._add_suffix_line.text())

        if len(sel) <= 0:
            tpRenamer.logger.warning('Renamer: You have to select at least one object')
        elif suffix == '':
            pass
        else:
            for obj in sel:
                new_name = "%s_%s" % (obj, suffix)
                maya.cmds.rename(obj, new_name)
                tpRenamer.logger.debug('Sucesfully renamed ' + str(len(sel)) + ' node(s)!')

    def _update_hierarchy_cbx(self):
        if self._all_radio.isChecked():
            self._hierarchy_cbx.setEnabled(False)
        else:
            self._hierarchy_cbx.setEnabled(True)

    def _get_rename_settings(self):

        text = str(self._renamer_line.text()).strip()

        naming_method = bool(self._renamer_mult_method_combo.currentIndex())
        padding = 0
        upper = True

        if naming_method == 0:
            padding = self._frame_pad_spin.value()
        else:
            upper = self._upper_radio.isChecked()

        prefix = ''
        suffix = ''

        if self._prefix_check.isChecked():
            prefix = self._prefix_line.text()
        if self._suffix_check.isChecked():
            suffix = self._suffix_line.text()

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

        joint_end = self._last_joint_is_end_cbx.isChecked()

        return text, prefix, suffix, padding, naming_method, upper, side, joint_end

    def _update_example_rename(self):
        """
        Method that updates the example line edit
        """

        example_text = ''

        text, prefix, suffix, padding, naming_method, upper, side, joint_end = self._get_rename_settings()

        if not text:
            self._renamer_lbl.setText('<font color=#646464>e.g.</font>')
            return

        if prefix:
            example_text += '%s_' % prefix

        if side != '':
            example_text += '%s_' % side

        example_text += '%s_' % text

        if naming_method:
            if upper:
                example_text += 'A'
            else:
                example_text += 'a'
        else:
            example_text += (padding * '0') + '1'

        if suffix:
            example_text += '_%s' % suffix

        self._renamer_lbl.setText('<font color=#646464>e.g. \'%s\'</font>' % example_text)

    def _toggle_mult_naming_method(self, index):

        """
        Method that updates the status of the radio buttons considering which option es enabled
        """

        self._lower_radio.setVisible(index)
        self._upper_radio.setVisible(index)
        self._frame_pad_lbl.setVisible(not index)
        self._frame_pad_spin.setVisible(not index)

        self._update_example_rename()

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
                discard_nodes.extend(tp.Dcc.all_shapes_nodes(full_path=False))
            else:
                shape_nodes = list()
                for obj in nodes:
                    shapes = tp.Dcc.list_shapes(obj, full_path=False)
                    if shapes:
                        shape_nodes.extend(shapes)
                nodes.extend(shape_nodes)

        nodes = list(set(nodes))

        for obj in nodes:
            if obj in discard_nodes:
                continue
            item = QTreeWidgetItem(self._names_list, [obj])
            item.obj = obj
            item.preview_name = ''
            self._names_list.addTopLevelItem(item)

    def _update_materials_names_list(self, nodes):
        """
        Internal function that updates name list with current scene objects
        """

        pass

    def _update_layers_names_list(self, nodes):
        """
        Internal function that updates name list with current scene objects
        """

        pass

    def _update_assets_names_list(self, nodes):
        """
        Internal function that updates name list with current scene objects
        """

        pass

    def _update_files_names_list(self, nodes):
        """
        Internal function that updates name list with current scene objects
        """

        pass

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

        items = self._names_list.selectedItems()
        for item in items:
            pass

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

    def _on_auto_rename(self):

        rule_item = self._names_list.currentItem()
        if not rule_item:
            tpRenamer.logger.warning('Impossible to rename because currently selected naming rule is not valid!')
            return

        current_rule = nameit.NameIt.get_active_rule()
        nameit.NameIt.set_active_rule(name=rule_item.rule.name)

        values = dict()
        for key, w in self._token_widgets.items():
            if type(w) == list:
                if isinstance(w[0], QComboBox):
                    values[key] = w[0].currentText()
            elif isinstance(w, QLineEdit):
                values[key] = w.text()

        if 'id' in values:
            values.pop('id')

        auto_name = nameit.NameIt.solve(**values)

        if current_rule:
            nameit.NameIt.set_active_rule(name=current_rule.name)

        return self.auto_rename_nodes(auto_name=auto_name)
    # endregion


@undo_decorator
def rename(nodes, text,
           prefix=None,
           suffix=None,
           padding=0,
           letters=False,
           capital=False,
           side='',
           last_joint_is_end=False,
           auto_rename=False):
    """
    Method that renames a group of nodes
    @param nodes: list(str): Nodes to rename
    @param text: str: New base name
    @param prefix: str, Prefix for the nodes
    @param suffix: str, Suffix for the nodes
    @param padding: int, Padding for the characters/numbers
    @param letters: bool, True if we want to use letters when renaming multiple nodes
    @param capital: bool, True if we want letters to be capital
    @param side: str, Side of the node
    @param last_joint_is_end: bool, True if the last node is an end node
    @param auto_rename: bool, True if we want to rename object using auto rename method
    """

    if prefix:
        if side != '':
            text = '%s_%s_%s' % (prefix, side, text)
        else:
            text = '%s_%s' % (prefix, text)

    # if single node, try without letter or number
    if len(nodes) == 1:

        node = nodes[0]
        new_name = text

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            if new_name:
                if 'none' in new_name:
                    type_part = nameit.NameIt.parse_field_from_string(new_name, 'type')
                    if type_part is None or (type_part and type_part == 'none'):
                        from tpRigToolkit.maya.lib import node as node_lib

                        types_dict = node_lib.get_node_types(node)
                        node_type = types_dict[node][0]

                        token_values = nameit.NamingData.get_tokens()
                        found_value = None
                        for token in token_values:
                            if token.name == 'type':
                                if node_type in token.values['key']:
                                    index = int(token.values['key'].index(node_type))
                                    found_value = token.values['value'][index]
                                    break

                        if found_value:
                            new_name = new_name.replace('none', found_value)
                        else:
                            new_name = new_name.replace('none', types_dict[node][0])

        if auto_rename:
            if node == new_name:
                return new_name
        else:
            if suffix:
                new_name += '_' + suffix
            if node == new_name:
                return new_name

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            if not maya.cmds.objExists(new_name):
                try:
                    maya.cmds.rename(node, new_name)
                except RuntimeError:
                    raise RenameException(node)
                return new_name
        else:
            raise NotImplementedError()

    # Rename nodes to tmp
    new_node_names = []
    failed_nodes = []
    for i, node in enumerate(reversed(nodes)):
        try:
            new_node_names.insert(0, maya.cmds.rename(node, '__tmp__' + str(i)))
        except RuntimeError:
            failed_nodes.insert(0, node)

    # Get new names
    new_nodes = []
    for node_name in new_node_names:

        new_name = None
        if auto_rename:
            if 'none' in text:
                type_part = nameit.NameIt.parse_field_from_string(text, 'type')
                if type_part is None or (type_part and type_part == 'none'):
                    from tpRigToolkit.maya.lib import node as node_lib

                    types_dict = node_lib.get_node_types(node_name)
                    node_type = types_dict[node_name][0]

                    token_values = nameit.NamingData.get_tokens()
                    found_value = None
                    for token in token_values:
                        if token.name == 'type':
                            if node_type in token.values['key']:
                                index = int(token.values['key'].index(node_type))
                                found_value = token.values['value'][index]
                                break

                    if found_value:
                        new_name = text.replace('none', found_value)
                    else:
                        new_name = text.replace('none', types_dict[node][0])

            if new_name:
                new_name = naming.FindUniqueName(new_name).get()
            else:
                new_name = naming.FindUniqueName(text).get()
        else:
            if tp.Dcc.get_name() == tp.Dccs.Maya:
                new_name = naming.find_available_name(text, suffix, 1, padding, letters, capital)
            else:
                new_name = text

        if not auto_rename:
            if last_joint_is_end and node_name == new_node_names[-1]:
                new_name += 'End'
        try:
            new_nodes.append(maya.cmds.rename(node_name, new_name))
        except RuntimeError:
            failed_nodes.append(node)

    if failed_nodes:
        raise RenameException(failed_nodes)

    return new_nodes


@undo_decorator
def replace(nodes, find_text, replace_text):
    if tp.Dcc.get_name() == tp.Dccs.Maya:
        shapes = maya.cmds.ls(nodes, s=True)
        shape_set = set(shapes)

        new_nodes_names = [];
        failed_nodes = []

        for i, node in enumerate(reversed(nodes)):

            if not find_text in node: continue
            if node in shape_set:     continue

            try:
                new_nodes_names.append((node, maya.cmds.rename(node, '__tmp__' + str(i))))
            except RuntimeError:
                failed_nodes.append(node)

        for i, shape in enumerate(shapes):
            if not find_text in shape: continue
            if not maya.cmds.objExists(shape):
                try:
                    new_name = maya.cmds.rename(shape, shape.replace(find_text, '__tmp__' + str(i)))
                    new_nodes_names.append((shape, new_name))
                except RuntimeError:
                    failed_nodes.append(node)

        new_names = []

        for name, new_node in new_nodes_names:
            new_name = name.replace(find_text, replace_text)
            if '|' in new_name:
                new_name = new_name.split('|')[-1]
            new_names.append(maya.cmds.rename(new_node, new_name))

        return new_names
    else:
        raise NotImplementedError()


def run():
    win = Renamer()
    win.show()
    return win
