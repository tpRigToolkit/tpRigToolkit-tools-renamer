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

import tpDccLib as tp
from tpPyUtils import decorators, strings
from tpQtLib.core import base, window
from tpQtLib.widgets import splitters, stack

if tp.is_maya():
    import tpMayaLib as maya
    from tpMayaLib.core import decorators as maya_decorators
    undo_decorator = maya_decorators.undo
else:
    undo_decorator = decorators.empty_decorator

from tpNameIt.core import namelib

import tpRenamer


class Renamer(window.MainWindow, object):
    def __init__(self):
        super(Renamer, self).__init__(
            name='RenamerBaseWindow',
            title='Renamer',
            size=(350, 700),
            fixed_size=False,
            auto_run=True,
            frame_less=True,
            use_style=False
        )

        self.setWindowIcon(tpRenamer.resource.icon('rename'))

    def ui(self):
        super(Renamer, self).ui()

        self._renamer_widget = RenamerWidget()
        self.main_layout.addWidget(self._renamer_widget)


class RenamerWidget(base.BaseWidget, object):

    NAMING_LIB = namelib.NameLib

    def __init__(self, config=None, parent=None):
        self._name_lib = self.NAMING_LIB()
        self._config = config or tpRenamer.configs_manager.get_config('renamer')
        super(RenamerWidget, self).__init__(parent=parent)

    def ui(self):
        super(RenamerWidget, self).ui()

        from tpRenamer.widgets import manualrenamewidget, autorenamewidget

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        self._top_layout.addLayout(self._categories_layout)

        self._top_layout.addWidget(splitters.get_horizontal_separator_widget())
        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(4, 0, 4, 0)
        selection_layout.setSpacing(2)
        self._top_layout.addLayout(selection_layout)

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
        self._splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(self._splitter)

        self.rename_tab = QTabWidget()
        self._splitter.addWidget(self.rename_tab)

        self.manual_rename_widget = manualrenamewidget.ManualRenameWidget()
        self.auto_rename_widget = autorenamewidget.AutoRenameWidget(naming_lib=self._name_lib)

        self.rename_tab.addTab(self.manual_rename_widget, 'Manual')
        self.rename_tab.addTab(self.auto_rename_widget, 'Auto')

        self._stack = stack.SlidingStackedWidget()
        self._splitter.addWidget(self._stack)

        no_items_widget = QFrame()
        no_items_widget.setFrameShape(QFrame.StyledPanel)
        no_items_widget.setFrameShadow(QFrame.Sunken)
        no_items_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        no_items_layout = QVBoxLayout()
        no_items_layout.setContentsMargins(0, 0, 0, 0)
        no_items_layout.setSpacing(0)
        no_items_widget.setLayout(no_items_layout)
        no_items_lbl = QLabel()
        no_items_pixmap = tpRenamer.resource.pixmap('no_items')
        no_items_lbl.setPixmap(no_items_pixmap)
        no_items_lbl.setAlignment(Qt.AlignCenter)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        no_items_layout.addWidget(no_items_lbl)
        no_items_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))

        self._stack.addWidget(no_items_widget)

        self._setup_categories()

    def setup_signals(self):
        self._stack.animFinished.connect(self._on_stack_anim_finished)
        self.rename_tab.currentChanged.connect(self._on_tab_changed)
        self._all_radio.clicked.connect(self._on_refresh_category)
        self._selected_radio.clicked.connect(self._on_refresh_category)
        self._hierarchy_cbx.toggled.connect(self._on_toggle_hierarchy_cbx)
        self.manual_rename_widget.renameUpdate.connect(self.update_current_items)
        self.manual_rename_widget.replaceUpdate.connect(self.update_current_items)
        self.auto_rename_widget.renameUpdated.connect(self.update_current_items)

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

    def _setup_categories(self):

        from tpRenamer.widgets import categorywidget

        if not self._config:
            tpRenamer.logger.warning(
                'Impossible to setup categories because tpRenamer configuration file is not available!')
            return

        categories = self._config.get('categories', default=list())
        if not categories:
            tpRenamer.logger.warning(
                'Impossible to setup categories because categories property is not defined in tpRenamer '
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
                    category_btn.setIcon(tpRenamer.resource.icon(icon))
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

    def _find_manual_available_name(self, items, name, prefix=None, suffix=None, side='', index=-1, padding=0, letters=False, capital=False, remove_first=0, remove_last=0, find_str=None, replace_str=None, joint_end=False):
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

        item_names = [item.obj for item in items]

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

                if generate_preview_name:

                    if base_name == item.obj and (prefix or suffix or side):
                        index = None
                    else:
                        index = duplicated_names[base_name]

                    preview_name = self._find_manual_available_name(items, base_name, prefix=prefix, side=side, suffix=suffix,
                                                                    index=index, padding=padding,
                                                                    letters=naming_method, capital=upper, joint_end=joint_end,
                                                                    remove_first=remove_first, remove_last=remove_last,
                                                                    find_str=find_str, replace_str=replace_str)

                    while preview_name in generated_names:
                        duplicated_names[base_name] += 1
                        preview_name = self._find_manual_available_name(items, base_name, prefix=prefix, side=side, suffix=suffix,
                                                                        index=duplicated_names[base_name], padding=padding,
                                                                        letters=naming_method, capital=upper, joint_end=joint_end,
                                                                        remove_first=remove_first, remove_last=remove_last,
                                                                        find_str=find_str, replace_str=replace_str)
                else:
                    preview_name = base_name

                item.preview_name = preview_name
                generated_names.append(preview_name)
        else:
            data = self.auto_rename_widget.get_rename_settings()

            for i, item in enumerate(items):
                data['id'] = i
                preview_name = self._name_lib.solve(**data)
                item.preview_name = preview_name

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
    def _on_rename(self):
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
                            tpRenamer.logger.warning('Impossible to rename: {} > {} | {}'.format(
                                full_name, item.preview_name, exc
                            ))
                else:
                    tp.Dcc.rename_node(item.full_name, item.preview_name)
                    item.obj = item.preview_name
                    item.preview_name = ''
            except Exception as e:
                tpRenamer.logger.warning('Impossible to rename: {} to {}'.format(item.full_name, item.preview_name))
                tpRenamer.logger.error('{} | {}'.format(e, traceback.format_exc()))

        self.update_current_items()
        names_list.clearSelection()


def run():
    win = Renamer()
    win.show()
    return win
