#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fully featured renamer tool
"""

from __future__ import print_function, division, absolute_import

import traceback
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import decorators, strings
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import splitter, splitters, stack
from tpDcc.libs.nameit.core import namelib
from tpDcc.tools.renamer.widgets import manualrenamewidget, autorenamewidget, categorywidget


if tp.is_maya():
    import tpDcc.dccs.maya as maya
    from tpDcc.dccs.maya.core import namespace, decorators as maya_decorators
    undo_decorator = maya_decorators.undo
else:
    undo_decorator = decorators.empty_decorator


logger = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


class RenamerWidget(base.BaseWidget, object):

    NAMING_LIB = namelib.NameLib

    def __init__(self, config=None, naming_config=None, parent=None):
        self._name_lib = self.NAMING_LIB()
        self._naming_config = naming_config
        if not self._naming_config:
            self._naming_config = tp.ConfigsMgr().get_config(config_name='tpDcc-naming')
        self._config = config or tp.ToolsMgr().get_tool_config('tpDcc-tools-renamer')
        super(RenamerWidget, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(RenamerWidget, self).ui()

        self._top_layout = QHBoxLayout()
        self._top_layout.setAlignment(Qt.AlignLeft)
        self._top_layout.setContentsMargins(2, 2, 2, 2)
        self._top_layout.setSpacing(2)
        self._buttons_grp = QButtonGroup(self)
        self._buttons_grp.setExclusive(True)
        self.main_layout.addLayout(self._top_layout)
        self.main_layout.addLayout(splitters.SplitterLayout())

        self._categories_layout = QHBoxLayout()
        self._categories_layout.setAlignment(Qt.AlignLeft)
        self._categories_layout.setContentsMargins(2, 2, 2, 2)
        self._categories_layout.setSpacing(2)

        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(4, 0, 4, 0)
        selection_layout.setSpacing(2)
        self._top_layout.addLayout(selection_layout)

        self._all_radio = QRadioButton('All')
        self._all_radio.setFixedHeight(19)
        self._all_radio.setAutoExclusive(True)
        self._selected_radio = QRadioButton('Selected')
        self._selected_radio.setFixedHeight(19)
        self._selected_radio.setChecked(True)
        self._selected_radio.setAutoExclusive(True)
        self._hierarchy_cbx = QCheckBox('Hierarchy')
        self._hierarchy_cbx.setFixedHeight(19)
        self._node_types_combo = QComboBox()
        self._node_types_combo.setMinimumWidth(120)
        self._auto_rename_shapes_cbx = None
        if tp.is_maya():
            self._auto_rename_shapes_cbx = QCheckBox('Auto Rename Shapes')
            self._auto_rename_shapes_cbx.setChecked(True)

        selection_layout.addWidget(self._selected_radio)
        selection_layout.addWidget(self._all_radio)
        selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        selection_layout.addWidget(self._hierarchy_cbx)
        selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
        selection_layout.addWidget(self._node_types_combo)
        if self._auto_rename_shapes_cbx:
            selection_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Fixed))
            selection_layout.addWidget(self._auto_rename_shapes_cbx)

        self._splitter = splitter.CollapsibleSplitter()
        self._splitter.setOrientation(Qt.Horizontal)
        self._splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(self._splitter)

        self.rename_tab = QTabWidget()
        self._splitter.addWidget(self.rename_tab)

        self.manual_rename_widget = manualrenamewidget.ManualRenameWidget()
        self.auto_rename_widget = autorenamewidget.AutoRenameWidget(naming_lib=self._name_lib)

        self.rename_tab.addTab(self.manual_rename_widget, 'Manual')
        self.rename_tab.addTab(self.auto_rename_widget, 'Auto')

        self._stack = stack.SlidingStackedWidget()

        splitter_right_widget = QWidget()
        splitter_right_layout = QVBoxLayout()
        splitter_right_layout.setContentsMargins(0, 0, 0, 0)
        splitter_right_layout.setSpacing(0)
        splitter_right_layout.addLayout(self._categories_layout)
        splitter_right_layout.addWidget(self._stack)
        splitter_right_widget.setLayout(splitter_right_layout)
        self._splitter.addWidget(splitter_right_widget)

        no_items_widget = QFrame()
        no_items_widget.setFrameShape(QFrame.StyledPanel)
        no_items_widget.setFrameShadow(QFrame.Sunken)
        no_items_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        no_items_layout = QVBoxLayout()
        no_items_layout.setContentsMargins(0, 0, 0, 0)
        no_items_layout.setSpacing(0)
        no_items_widget.setLayout(no_items_layout)
        no_items_lbl = QLabel()
        no_items_pixmap = tp.ResourcesMgr().pixmap('no_items')
        no_items_lbl.setPixmap(no_items_pixmap)
        no_items_lbl.setAlignment(Qt.AlignCenter)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        no_items_layout.addWidget(no_items_lbl)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        self._stack.addWidget(no_items_widget)

        self._setup_categories()

        self._splitter.handle(0).collapse()
        self._splitter.setSizes([1, 0])

    def setup_signals(self):
        self._stack.animFinished.connect(self._on_stack_anim_finished)
        self.rename_tab.currentChanged.connect(self._on_tab_changed)
        self._all_radio.clicked.connect(self._on_refresh_category)
        self._selected_radio.clicked.connect(self._on_refresh_category)
        self._hierarchy_cbx.toggled.connect(self._on_toggle_hierarchy_cbx)
        self.manual_rename_widget.renameUpdate.connect(self.update_current_items)
        self.manual_rename_widget.replaceUpdate.connect(self.update_current_items)
        self.manual_rename_widget.doName.connect(self._on_simple_rename)
        self.manual_rename_widget.doSearchReplace.connect(self._on_search_replace)
        self.manual_rename_widget.doAddPrefix.connect(self._on_add_prefix)
        self.manual_rename_widget.doAddSuffix.connect(self._on_add_suffix)
        self.manual_rename_widget.doRemovePrefix.connect(self._on_remove_prefix)
        self.manual_rename_widget.doRemoveSuffix.connect(self._on_remove_suffix)
        self.manual_rename_widget.doRemoveFirst.connect(self._on_remove_first)
        self.manual_rename_widget.doRemoveLast.connect(self._on_remove_last)
        self.manual_rename_widget.doReplacePadding.connect(self._on_replace_padding)
        self.manual_rename_widget.doAppendPadding.connect(self._on_append_padding)
        self.manual_rename_widget.doChangePadding.connect(self._on_change_padding)
        self.manual_rename_widget.doSide.connect(self._on_side)
        self.manual_rename_widget.doAddNamespace.connect(self._on_add_replace_namespace)
        self.manual_rename_widget.doRemoveNamespace.connect(self._on_remove_namespace)
        self.manual_rename_widget.doAutoSuffix.connect(self._on_auto_suffix)
        self.manual_rename_widget.doUniqueName.connect(self._on_unique_name)
        self.manual_rename_widget.doRemoveAllNumbers.connect(self._on_remove_all_numbers)
        self.manual_rename_widget.doRemoveTailNumbers.connect(self._on_remove_tail_numbers)
        self.manual_rename_widget.doRename.connect(self._on_simple_rename)
        self.auto_rename_widget.renameUpdated.connect(self.update_current_items)
        self.auto_rename_widget.doRename.connect(self._on_auto_rename)

    def keyPressEvent(self, event):

        # Prevent lost focus when writing on QLineEdits
        if event.key() in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_CapsLock):
            event.accept()
        else:
            event.ignore()

    def update_current_items(self):
        """
        Function that updates the names of the current selected items
        """

        self._update_current_objects_items()

    def refresh(self):
        """
        Refresh UI data
        """

        self._update_node_types()

    def _setup_categories(self):
        if not self._config:
            logger.warning(
                'Impossible to setup categories because tpDcc-tools-renamer configuration file is not available!')
            return

        categories = self._config.get('categories', default=list())
        if not categories:
            logger.warning(
                'Impossible to setup categories because categories property is not defined in tpDcc-tools-renamer '
                'configuration file!')
            return

        for i, category in enumerate(categories):
            for category_name, category_data in category.items():
                title = category_data.get('title', category)
                icon = category_data.get('icon', None)
                types = category_data.get('types', dict())
                nodes_to_discard = self._get_nodes_to_discard()

                category_btn = QPushButton(title)
                category_btn.setMinimumWidth(55)
                category_btn.setCheckable(True)
                if icon:
                    category_btn.setIcon(tp.ResourcesMgr().icon(icon))
                if i == 0:
                    category_btn.setChecked(True)
                self._buttons_grp.addButton(category_btn)
                self._categories_layout.addWidget(category_btn)
                category_widget = categorywidget.CategoryWidget(types=types, nodes_to_discard=nodes_to_discard)
                self._stack.addWidget(category_widget)

                category_widget.doRefresh.connect(self._on_refresh_category)
                category_widget.doPreview.connect(self._set_preview_names)
                category_widget.togglePreview.connect(self.update_current_items)
                category_widget.doRename.connect(self._on_rename)
                category_btn.clicked.connect(partial(self._on_category_selected, i+1))

        if self._stack.count() > 1:
            self._on_category_selected(1)

    def _update_node_types(self):
        """
        Internal function that updates the list of availble types
        """

        self._node_types_combo.clear()

        dcc_types = tp.Dcc.TYPE_FILTERS.keys()
        if not dcc_types:
            self._node_types_combo.setVisible(False)
        else:
            self._node_types_combo.setVisible(True)
            for node_type in dcc_types:
                self._node_types_combo.addItem(node_type)

    def _get_nodes_to_discard(self):
        """
        Internal function that updates name list with current scene objects
        """

        discard_nodes = self._config.get('nodes_to_discard', default=list())
        types_to_discard = self._config.get('types_to_discard', default=list())
        for node_type in types_to_discard:
            discard_nodes.extend(tp.Dcc.list_nodes(node_type=node_type))

        return discard_nodes

    def _update_current_objects_items(self):
        category_widget = self._stack.current_widget
        if not category_widget:
            return

        names_list = category_widget.get_names_list()
        for i in range(names_list.topLevelItemCount()):
            item = names_list.topLevelItem(i)
            item.preview_name = ''
            if hasattr(item, 'obj'):
                item.setText(0, item.obj)

        if category_widget.is_preview_enabled():
            selected_items = names_list.selectedItems()
            self._set_preview_names(items=selected_items)

    def _find_manual_available_name(self, items, name, prefix=None, suffix=None, side='', index=-1, padding=0,
                                    letters=False, capital=False, remove_first=0, remove_last=0, find_str=None,
                                    replace_str=None, joint_end=False):
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
                test_name = '{}_{}'.format(test_name, str(index).zfill(padding))

        if suffix:
            test_name = '{}_{}'.format(test_name, suffix)

        if remove_first and remove_first > 0:
            test_name = test_name[remove_first:]

        if remove_last and remove_last > 0:
            test_name = test_name[:-remove_last]

        if find_str != None and find_str != '' and replace_str != None:
            test_name = test_name.replace(find_str, replace_str)

        item_names = list()
        for item in items:
            if hasattr(item, 'obj'):
                item_names.append(item.obj)
            else:
                item_names.append(item)

        # if object exists, try next index
        if tp.Dcc.object_exists(test_name) or test_name in item_names:
            new_index = int(index) + 1
            return self._find_manual_available_name(
                items, name, prefix=prefix, index=new_index, padding=padding,
                letters=letters, capital=capital, remove_first=remove_first, remove_last=remove_last,
                joint_end=joint_end, find_str=find_str, replace_str=replace_str
            )

        return test_name

    def _generate_preview_names(self, items):

        # Manual Rename
        if self.rename_tab.currentIndex() == 0:

            text, prefix, suffix, padding, naming_method, upper, side, remove_first, remove_last, joint_end = self.manual_rename_widget.get_rename_settings()
            find_str, replace_str = self.manual_rename_widget.get_replace_settings()

            duplicated_names = dict()
            generated_names = list()

            for item in items:
                if not text:
                    if hasattr(item, 'obj'):
                        base_name = item.obj
                    else:
                        base_name = item
                else:
                    base_name = text

                if hasattr(item, 'obj'):
                    item_obj = item.obj
                else:
                    item_obj = item

                if base_name == item_obj and not prefix and not suffix and not side:
                    generate_preview_name = False
                else:
                    generate_preview_name = True
                if base_name in duplicated_names:
                    duplicated_names[base_name] += 1
                else:
                    duplicated_names[base_name] = 0

                if generate_preview_name:
                    if base_name == item_obj and (prefix or suffix or side):
                        index = None
                    else:
                        index = duplicated_names[base_name]

                    preview_name = self._find_manual_available_name(
                        items, base_name, prefix=prefix, side=side, suffix=suffix,
                        index=index, padding=padding, letters=naming_method, capital=upper, joint_end=joint_end,
                        remove_first=remove_first, remove_last=remove_last, find_str=find_str, replace_str=replace_str)

                    while preview_name in generated_names:
                        duplicated_names[base_name] += 1
                        preview_name = self._find_manual_available_name(
                            items, base_name, prefix=prefix, side=side, suffix=suffix,
                            index=duplicated_names[base_name], padding=padding, letters=naming_method, capital=upper,
                            joint_end=joint_end, remove_first=remove_first, remove_last=remove_last, find_str=find_str,
                            replace_str=replace_str)
                else:
                    preview_name = base_name

                if not isinstance(item, (str, unicode)):
                    item.preview_name = preview_name
                generated_names.append(preview_name)

            return generated_names

        else:
            data = self.auto_rename_widget.get_rename_settings()

            for i, item in enumerate(items):
                data['id'] = i
                preview_name = self._name_lib.solve(**data)
                item.preview_name = preview_name

    def _get_filter_vars(self):
        """
        Internal function that returns current filter variables
        """

        search_hierarchy = self._hierarchy_cbx.isChecked()
        only_selection = self._selected_radio.isChecked()

        return search_hierarchy, only_selection

    def _get_filter_type(self):
        """
        Returns filter type selected by user
        :return: str or None
        """

        filter_type = None
        if self._node_types_combo.currentText() in tp.Dcc.TYPE_FILTERS:
            filter_type = self._node_types_combo.currentText()

        return filter_type

    def _get_objects_to_rename(self):
        """
        Internal function that returns objects to rename depending on filter setup
        """

        search_hierarchy, search_selection = self._get_filter_vars()

        if not search_selection:
            objs_to_rename = tp.Dcc.all_scene_objects(full_path=True)
        else:
            objs_to_rename = tp.Dcc.selected_nodes(full_path=True)
        if not objs_to_rename:
            logger.warning('No objects to rename!')
        if search_hierarchy:
            children_list = list()
            for obj in objs_to_rename:
                children = tp.Dcc.list_children(obj, all_hierarchy=True, full_path=True)
                if children:
                    children_list.extend(children)
            children_list = list(set(children_list))
            objs_to_rename.extend(children_list)

        objs_to_rename = [obj for obj in objs_to_rename if tp.Dcc.node_type(obj) == 'transform']

        # We reverse the list so we update first children and later parents, otherwise we will have
        # problems during renaming if we use full paths
        # TODO: In Maya we can use OpenMaya handles or UUIDs to avoid this
        objs_to_rename.reverse()

        return objs_to_rename

    def _set_preview_names(self, items, do_preview=True):
        """
        Internal function that sets the preview name for the given items
        :param items:
        :return:
        """

        self._generate_preview_names(items)

        if do_preview:
            for item in items:
                if item.preview_name:
                    item.setText(0, item.preview_name)

    def _on_tab_changed(self, tab_index):

        if tab_index != 1:
            return

        self.auto_rename_widget.update_rules()

    def _on_toggle_hierarchy_cbx(self, flag):
        self._on_refresh_category()

    def _on_category_selected(self, index):
        if self._stack.currentIndex() == index:
            return

        for i, btn in enumerate(self._buttons_grp.buttons()):
            if i == index - 1:
                continue
            btn.setEnabled(False)
        self._stack.slide_in_index(index)

    def _on_stack_anim_finished(self, index):
        for btn in self._buttons_grp.buttons():
            btn.setEnabled(True)
        category_widget = self._stack.current_widget
        if not category_widget:
            return
        self._on_refresh_category(category_widget)

    def _on_refresh_category(self, category_widget=None):
        if not category_widget:
            category_widget = self._stack.current_widget
            if not category_widget:
                return

        category_widget.refresh(
            selected_objects=self._selected_radio.isChecked(), hierarchy=self._hierarchy_cbx.isChecked())

    @undo_decorator
    def _on_simple_rename(self, new_name=None):
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True
        if new_name:
            objs_to_rename = self._get_objects_to_rename() or list()
            for obj in objs_to_rename:
                try:
                    tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)
                except Exception as exc:
                    pass
        else:
            objs_to_rename = self._get_objects_to_rename() or list()
            if not objs_to_rename:
                logger.warning('No objects to rename. Please select at least one object!')
                return
            new_names = self._generate_preview_names(objs_to_rename)
            if len(objs_to_rename) != len(new_names):
                logger.warning('Impossible to retrieve valid renamed names. Rename nodes manually please!')
                return

            for obj, new_name in zip(objs_to_rename, new_names):
                tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)

    @undo_decorator
    def _on_rename(self):
        """
        Internal callback function that is called when the user presses the rename button
        """
        
        category_widget = self._stack.current_widget
        if not category_widget:
            return

        names_list = category_widget.get_names_list()
        items_to_rename = names_list.selectedItems()
        for item in items_to_rename:
            try:
                if hasattr(item, 'handle'):
                    if tp.is_maya():
                        mobj = item.handle.object()
                        try:
                            dag_path = maya.OpenMaya.MDagPath.getAPathTo(mobj)
                            full_name = dag_path.fullPathName()
                        except Exception:
                            full_name = item.full_name
                        try:
                            tp.Dcc.rename_node(full_name, item.preview_name)
                            item.obj = item.preview_name
                            item.preview_name = ''
                        except Exception as exc:
                            logger.warning('Impossible to rename: {} > {} | {}'.format(
                                full_name, item.preview_name, exc
                            ))
                else:
                    tp.Dcc.rename_node(item.full_name, item.preview_name)
                    item.obj = item.preview_name
                    item.preview_name = ''
            except Exception as e:
                logger.warning('Impossible to rename: {} to {}'.format(item.full_name, item.preview_name))
                logger.error('{} | {}'.format(e, traceback.format_exc()))

        self.update_current_items()
        names_list.clearSelection()

    @undo_decorator
    def _on_auto_rename(self, rule_name, tokens_dict):

        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True
        objs_to_rename = self._get_objects_to_rename() or list()
        if not objs_to_rename:
            logger.warning('No objects to rename. Please select at least one object!')
            return

        if not self._name_lib.has_rule(rule_name):
            return
        current_rule = self._name_lib.active_rule()

        self._name_lib.set_active_rule(rule_name)
        token_dict = dict()
        for token_name, token_data in tokens_dict.items():
            token_value_fn = token_data['fn']
            token_value = token_value_fn()
            token_dict[token_name] = token_value

        # TODO: Naming config should be define the name of the rule to use when using auto renaming
        solved_names = dict()
        if rule_name == 'node' and self._naming_config:
            auto_suffix = self._naming_config.get('auto_suffixes', default=dict())
            if auto_suffix:
                solved_names = dict()
                for obj_name in objs_to_rename:
                    obj_uuid = maya.cmds.ls(obj_name, uuid=True)[0]
                    if obj_uuid in solved_names:
                        tp.logger.warning(
                            'Node with name: "{} and UUID "{}" already renamed to "{}"! Skipping ...'.format(
                                obj_name, obj_uuid, solved_names[obj_name]))
                        continue

                    # TODO: This code is a duplicated version of the one in
                    #  tpDcc.dccs.maya.core.name.auto_suffix_object function. Move this code to a DCC specific function
                    obj_type = maya.cmds.objectType(obj_name)
                    if obj_type == 'transform':
                        shape_nodes = maya.cmds.listRelatives(obj_name, shapes=True, fullPath=True)
                        if not shape_nodes:
                            obj_type = 'group'
                        else:
                            obj_type = maya.cmds.objectType(shape_nodes[0])
                    elif obj_type == 'joint':
                        shape_nodes = maya.cmds.listRelatives(obj_name, shapes=True, fullPath=True)
                        if shape_nodes and maya.cmds.objectType(shape_nodes[0]) == 'nurbsCurve':
                            obj_type = 'controller'
                    if obj_type == 'nurbsCurve':
                        connections = maya.cmds.listConnections('{}.message'.format(obj_name))
                        if connections:
                            for node in connections:
                                if maya.cmds.nodeType(node) == 'controller':
                                    obj_type = 'controller'
                                    break
                    if obj_type not in auto_suffix:
                        rule_name = 'node'
                        node_type = obj_type
                    else:
                        rule_name = auto_suffix[obj_type]
                        node_type = auto_suffix[obj_type]

                    if 'node_type' in token_dict:
                        token_dict.pop('node_type')
                    if 'description' in token_dict:
                        token_dict.pop('description')
                    node_name = tp.Dcc.node_short_name(obj_name)
                    solved_name = self._name_lib.solve(node_name, node_type=node_type)
                    if not solved_name:
                        continue
                    solved_names[obj_uuid] = solved_name

        if solved_names:
            for obj_id, solved_name in solved_names.items():
                obj_name = maya.cmds.ls(obj_id, long=True)[0]
                tp.Dcc.rename_node(obj_name, solved_name, uuid=obj_id, rename_shape=rename_shape)
        else:
            for obj_name in objs_to_rename:
                solve_name = self._name_lib.solve(**token_dict)
                if not solve_name:
                    tp.logger.warning(
                        'Impossible to rename "{}" with rule "{}" | "{}"'.format(obj_name, rule_name, token_dict))
                    continue
                try:
                    tp.Dcc.rename_node(obj_name, solve_name, rename_shape=rename_shape)
                except Exception as exc:
                    tp.logger.error('Impossible to rename "{}" to "{}" | {}'.format(obj_name, solve_name, exc))
                    continue

            if current_rule:
                self._name_lib.set_active_rule(current_rule.name)

    @undo_decorator
    def _on_search_replace(self, search_text, replace_text):
        objs_to_rename = self._get_objects_to_rename() or list()
        for obj in objs_to_rename:
            try:
                obj_short_name = tp.Dcc.node_short_name(obj)
                new_name = obj_short_name.replace(search_text, replace_text)
                tp.Dcc.rename_node(obj, new_name)
            except Exception as exc:
                pass

    @undo_decorator
    def _on_add_prefix(self, prefix_text):
        """
        Internal callback function that is called when the user presses the add prefix button
        :param prefix_text: str, prefix to add
        """
        
        if not prefix_text:
            return
        if tp.is_maya():
            # First letter as digit is not supported in Maya
            if prefix_text[0].isdigit():
                return

        search_hierarchy, selection_only = self._get_filter_vars()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        dcc_type = None
        if self._node_types_combo.currentText() in tp.Dcc.TYPE_FILTERS:
            dcc_type = self._node_types_combo.currentText()
        
        return tp.Dcc.add_name_prefix(
            prefix=prefix_text, filter_type=dcc_type, search_hierarchy=search_hierarchy, selection_only=selection_only,
            rename_shape=rename_shape)

    @undo_decorator
    def _on_add_suffix(self, suffix_text):
        """
        Internal callback function that is called when the user presses the add suffix button
        :param suffix_text: str, suffix to add
        """
        
        if not suffix_text:
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.add_name_suffix(
            suffix=suffix_text, filter_type=filter_type, search_hierarchy=search_hierarchy,
            selection_only=selection_only, rename_shape=rename_shape)

    @undo_decorator
    def _on_remove_prefix(self):
        """
        Internal callback function that is called when the user presses the remove prefix button
        """
        
        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Remove Prefix must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.remove_name_prefix(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only,
            rename_shape=rename_shape)

    @undo_decorator
    def _on_remove_suffix(self):
        """
        Internal callback function that is called when the user presses the remove suffix button
        """

        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Remove Suffix must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.remove_name_suffix(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only,
            rename_shape=rename_shape)

    @undo_decorator
    def _on_remove_first(self, num_to_remove):
        """
        Internal callback function that is called when the user presses the remove first button
        :param num_to_remove: int, number of characters to remove
        """

        if not num_to_remove or not num_to_remove > 0:
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Remove Suffix must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True
        filtered_obj_list = tp.Dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            new_name = obj[num_to_remove+1:]
            tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)
    
    @undo_decorator
    def _on_remove_last(self, num_to_remove):
        """
        Internal callback function that is called when the user presses the remove last button
        :param num_to_remove: int, number of characters to remove
        """

        if not num_to_remove or not num_to_remove > 0:
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Remove Suffix must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True
        filtered_obj_list = tp.Dcc.filter_nodes_by_type(
            filter_type=filter_type, search_hierarchy=search_hierarchy, selection_only=selection_only)

        for obj in filtered_obj_list:
            new_name = obj[:-num_to_remove]
            tp.Dcc.rename_node(obj, new_name, rename_shape=rename_shape)

    @undo_decorator
    def _on_replace_padding(self, pad):
        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Replace Padding must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.renumber_objects(
            filter_type=filter_type, remove_trailing_numbers=True, padding=int(pad), add_underscore=True,
            rename_shape=rename_shape, search_hierarchy=search_hierarchy, selection_only=selection_only)

    @undo_decorator
    def _on_append_padding(self, pad):
        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Replace Padding must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.renumber_objects(
            filter_type=filter_type, remove_trailing_numbers=False, padding=int(pad), add_underscore=True,
            rename_shape=rename_shape, search_hierarchy=search_hierarchy, selection_only=selection_only)

    @undo_decorator
    def _on_change_padding(self, pad):
        search_hierarchy, selection_only = self._get_filter_vars()
        if not search_hierarchy and not selection_only:
            tp.logger.warning('Replace Padding must be used with "Selected" option not with "All"')
            return None

        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.change_suffix_padding(
            filter_type=filter_type, padding=int(pad), add_underscore=True, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only)

    @undo_decorator
    def _on_side(self, side):
        if not side:
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.add_name_suffix(
            suffix=side, filter_type=filter_type, search_hierarchy=search_hierarchy, add_underscore=True,
            selection_only=selection_only, rename_shape=rename_shape)

    @undo_decorator
    def _on_add_replace_namespace(self, namespace_to_add):

        if not tp.is_maya() or not namespace_to_add:
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return namespace.assign_namespace_to_object_by_filter(
            namespace=namespace_to_add, filter_type=filter_type, force_create=True, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only, dag=False, remove_maya_defaults=True,
            transforms_only=True)

    @undo_decorator
    def _on_remove_namespace(self, namespace_to_remove=None):

        if not tp.is_maya():
            return

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        if not namespace_to_remove:
            raise NotImplementedError('Removing namespace from selection is not supported yet!')

        return namespace.remove_namespace_from_object_by_filter(
            namespace=namespace_to_remove, filter_type=filter_type, rename_shape=rename_shape,
            search_hierarchy=search_hierarchy, selection_only=selection_only, dag=False, remove_maya_defaults=True,
            transforms_only=True)

    @undo_decorator
    def _on_auto_suffix(self):

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.auto_name_suffix(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

    @undo_decorator
    def _on_unique_name(self):

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.find_unique_name(
            filter_type=filter_type, do_rename=True, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only)

    @undo_decorator
    def _on_remove_all_numbers(self):

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.remove_name_numbers(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only, trailing_only=False)

    @undo_decorator
    def _on_remove_tail_numbers(self):

        search_hierarchy, selection_only = self._get_filter_vars()
        filter_type = self._get_filter_type()
        rename_shape = self._auto_rename_shapes_cbx.isChecked() if self._auto_rename_shapes_cbx else True

        return tp.Dcc.remove_name_numbers(
            filter_type=filter_type, rename_shape=rename_shape, search_hierarchy=search_hierarchy,
            selection_only=selection_only, trailing_only=True)
