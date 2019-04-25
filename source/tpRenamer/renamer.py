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
from tpQtLib.Qt.QtGui import *

import tpRenamer
import tpDccLib as tp
from tpPyUtils import decorators, qtutils
from tpQtLib.core import window
from tpQtLib.widgets import splitters, expandables, button

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


class RenameException(Exception):
    """
    Custom exception class that will handle errors when renaming elements using tpRenamer tool
    """

    def __init__(self, nodes):

        error_text = '======= Renamer: Failed to rename one or more nodes ======='
        if not hasattr(nodes, '__iter__'):
            nodes = [nodes]
        for node in nodes:
            if tp.Dcc.get_name() == tp.Dccs.Maya:
                if not maya.cmds.objExists(node):
                    error_text += "\t'%s' no longer exists.\n" % node
                elif maya.cmds.lockNode(node, q=True, l=True):
                    error_text += "\t'%s' is locked.\n" % node
                else:
                    error_text += "\t'%s' failure unknows.\n" % node
            else:
                raise NotImplementedError()

        Exception.__init__(self, error_text)


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

    # region Static Functions
    @staticmethod
    def select_hierarchy():
        """
        Method that selects the hierarchy of the selected nodes
        """

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            sel = maya.cmds.ls(selection=True)

            for obj in sel:
                maya.cmds.select(obj, hi=True, add=True)
        else:
            raise NotImplementedError()
    # endregion

    # region Override Functions
    def ui(self):
        super(Renamer, self).ui()

        self.rename_tab = QTabWidget()

        manual_rename_layout = QVBoxLayout()
        manual_rename_widget = QWidget()
        manual_rename_widget.setLayout(manual_rename_layout)

        auto_rename_layout = QVBoxLayout()
        auto_rename_widget = QWidget()
        auto_rename_widget.setLayout(auto_rename_layout)

        self.rename_tab.addTab(manual_rename_widget, 'Manual')

        if NAMING_IT_AVAILABLE:
            self.rename_tab.addTab(auto_rename_widget, 'Auto')

        self.main_layout.addWidget(self.rename_tab)

        # === Renamer Widget === #

        renamer_expander = expandables.ExpanderWidget()
        renamer_expander.setDragDropMode(expandables.ExpanderDragDropModes.NoDragDrop)
        renamer_expander.setRolloutStyle(expandables.ExpanderStyles.Maya)
        manual_rename_layout.addWidget(renamer_expander)

        renamer_widget = QWidget()
        renamer_widget.setLayout(QVBoxLayout())
        renamer_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        renamer_widget.layout().setContentsMargins(0, 0, 0, 0)
        renamer_widget.layout().setSpacing(2)

        renamer_expander.addItem(title='RENAME', widget=renamer_widget, collapsed=False)

        renamer_text_layout = QHBoxLayout()
        renamer_text_layout.setContentsMargins(4, 0, 4, 0)
        renamer_text_layout.setSpacing(2)

        renamer_widget.layout().addLayout(renamer_text_layout)

        renamer_text_lbl = QLabel('New Name: ')
        self._renamer_line = QLineEdit()
        renamer_text_layout.addWidget(renamer_text_lbl)
        renamer_text_layout.addWidget(self._renamer_line)

        reg_ex = QRegExp("^(?!^_)[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._renamer_line)
        self._renamer_line.setValidator(text_validator)

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        rename_mult_layout = QHBoxLayout()
        rename_mult_layout.setContentsMargins(4, 0, 4, 0)
        rename_mult_layout.setSpacing(2)

        renamer_widget.layout().addLayout(rename_mult_layout)

        rename_mult_method_lbl = QLabel('Multiples Naming Method: ')
        self._renamer_mult_method_combo = QComboBox()
        self._renamer_mult_method_combo.addItem('Numbers (0-9)')
        self._renamer_mult_method_combo.addItem('Letters (a-z)')
        self._renamer_mult_method_combo.setFixedWidth(100)

        rename_mult_layout.addWidget(rename_mult_method_lbl)
        rename_mult_layout.addWidget(self._renamer_mult_method_combo)

        mult_options_layout = QHBoxLayout()
        mult_options_layout.setContentsMargins(4, 0, 4, 0)
        mult_options_layout.setSpacing(2)
        renamer_widget.layout().addLayout(mult_options_layout)

        self._frame_pad_lbl = QLabel('No. Padding: ')
        self._frame_pad_spin = QSpinBox()
        self._frame_pad_spin.setFixedWidth(40)
        self._frame_pad_spin.setMinimum(0)
        self._frame_pad_spin.setMaximum(10)

        self._lower_radio = QRadioButton('Lowercase')
        self._upper_radio = QRadioButton('Uppercase')
        self._lower_radio.setVisible(False)
        self._upper_radio.setVisible(False)
        self._lower_radio.setFixedHeight(19)
        self._upper_radio.setFixedHeight(19)
        self._lower_radio.setChecked(True)

        mult_options_layout.addWidget(self._frame_pad_lbl)
        mult_options_layout.addWidget(self._lower_radio)
        mult_options_layout.addItem(QSpacerItem(5, 5, QSizePolicy.Expanding))
        mult_options_layout.addWidget(self._frame_pad_spin)
        mult_options_layout.addWidget(self._upper_radio)

        fix_layout = QHBoxLayout()
        fix_layout.setContentsMargins(4, 0, 4, 0)
        fix_layout.setSpacing(2)

        renamer_widget.layout().addLayout(fix_layout)

        self._prefix_check = QCheckBox('Prefix: ')
        self._prefix_line = QLineEdit()
        self._prefix_line.setEnabled(False)
        self._prefix_line.setFixedWidth(85)
        self._prefix_line.setValidator(text_validator)

        self._suffix_check = QCheckBox('Suffix: ')
        self._suffix_line = QLineEdit()
        self._suffix_line.setEnabled(False)
        self._suffix_line.setFixedWidth(85)
        self._suffix_line.setValidator(text_validator)

        fix_layout.addWidget(self._prefix_check)
        fix_layout.addWidget(self._prefix_line)
        fix_layout.addItem(QSpacerItem(5, 5, QSizePolicy.Expanding))
        fix_layout.addWidget(self._suffix_check)
        fix_layout.addWidget(self._suffix_line)

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        side_layout = QHBoxLayout()
        side_layout.setContentsMargins(0, 2, 0, 0)
        side_layout.setSpacing(2)

        side_box = QGroupBox()
        side_box.setLayout(side_layout)
        side_box.setStyleSheet("border:0px;")

        renamer_widget.layout().addWidget(side_box)

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

        self._none_side.setChecked(True)

        self._capital_side = QCheckBox('Capital?')

        side_layout.addWidget(self._side_lbl)
        side_layout.addWidget(self._none_side)
        side_layout.addWidget(self._right_side)
        side_layout.addWidget(self._center_side)
        side_layout.addWidget(self._mid_side)
        side_layout.addWidget(self._left_side)

        renamer_widget.layout().addWidget(self._capital_side)

        renamer_widget.layout().addLayout(splitters.SplitterLayout())

        last_joint_layout = QVBoxLayout()
        renamer_widget.layout().addLayout(last_joint_layout)

        self._last_joint_is_end_cbx = QCheckBox('Last joint is an endJoint?')
        self._last_joint_is_end_cbx.setChecked(True)
        last_joint_layout.addWidget(self._last_joint_is_end_cbx)

        rename_btn_layout = QHBoxLayout()
        rename_btn_layout.setContentsMargins(4, 0, 4, 0)
        rename_btn_layout.setSpacing(0)

        renamer_widget.layout().addLayout(rename_btn_layout)

        self._renamer_lbl = QLabel('e.g. ')
        self._renamer_btn = QPushButton('Rename')
        self._renamer_btn.setFixedHeight(20)
        self._renamer_btn.setFixedWidth(55)

        rename_btn_layout.addWidget(self._renamer_lbl)
        rename_btn_layout.addWidget(self._renamer_btn)

        # ------------------------------------------------------------------------

        ### Replacer Widget ###

        replacer_expander = expandables.ExpanderWidget()
        replacer_expander.setDragDropMode(expandables.ExpanderDragDropModes.NoDragDrop)
        replacer_expander.setRolloutStyle(expandables.ExpanderStyles.Maya)
        manual_rename_layout.addWidget(replacer_expander)

        replacer_widget = QWidget()
        replacer_widget.setLayout(QVBoxLayout())
        replacer_widget.layout().setContentsMargins(0, 0, 0, 0)
        replacer_widget.layout().setSpacing(2)
        replacer_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        replacer_expander.addItem(title='FIND/REPLACE', widget=replacer_widget, )

        replace_lbl = QLabel('Find: ')
        self._replace_line = QLineEdit()
        with_lbl = QLabel('Replace: ')
        self._with_line = QLineEdit()
        replace_lbl.setFixedWidth(55)
        with_lbl.setFixedWidth(55)

        reg_ex = QRegExp("[a-zA-Z_0-9]+")
        text_validator = QRegExpValidator(reg_ex, self._replace_line)
        self._replace_line.setValidator(text_validator)
        self._with_line.setValidator(text_validator)

        replace_layout = QHBoxLayout()
        replace_layout.setContentsMargins(4, 0, 4, 0)
        replace_layout.setSpacing(2)
        replace_layout.addWidget(replace_lbl)
        replace_layout.addWidget(self._replace_line)
        with_layout = QHBoxLayout()
        with_layout.setContentsMargins(4, 0, 4, 0)
        with_layout.setSpacing(2)
        with_layout.addWidget(with_lbl)
        with_layout.addWidget(self._with_line)
        replacer_widget.layout().addLayout(replace_layout)
        replacer_widget.layout().addLayout(with_layout)

        replacer_widget.layout().addLayout(splitters.SplitterLayout())

        selection_layout = QHBoxLayout()
        selection_layout.setContentsMargins(4, 0, 4, 0)
        selection_layout.setSpacing(2)

        replacer_widget.layout().addLayout(selection_layout)

        selection_mode_lbl = QLabel('Selection Mode: ')
        self._all_radio = QRadioButton('All')
        self._all_radio.setFixedHeight(19)
        self._selected_radio = QRadioButton('Selected')
        self._selected_radio.setFixedHeight(19)
        self._selected_radio.setChecked(True)
        self._hierarchy_cbx = QCheckBox('Hierarchy')
        self._hierarchy_cbx.setFixedHeight(19)

        selection_layout.addWidget(selection_mode_lbl)
        spacer_item = QSpacerItem(5, 5, QSizePolicy.Expanding)
        selection_layout.addSpacerItem(spacer_item)
        selection_layout.addWidget(self._all_radio)
        selection_layout.addWidget(self._selected_radio)
        selection_layout.addWidget(self._hierarchy_cbx)

        replacer_widget.layout().addLayout(splitters.SplitterLayout())

        self._replace_btn = QPushButton('Replace')
        self._replace_btn.setFixedHeight(20)
        self._replace_btn.setFixedWidth(55)

        replace_btn_layout = QHBoxLayout()
        replace_btn_layout.setContentsMargins(4, 0, 4, 0)
        replace_btn_layout.setSpacing(0)
        replace_btn_layout.setAlignment(Qt.AlignRight)
        replace_btn_layout.addWidget(self._replace_btn)

        replacer_widget.layout().addLayout(replace_btn_layout)

        ### Add Prefix Widget ###
        add_prefix_widget = QWidget()
        add_prefix_widget.setLayout(QVBoxLayout())
        add_prefix_widget.layout().setContentsMargins(0, 0, 0, 0)
        add_prefix_widget.layout().setSpacing(2)
        add_prefix_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        add_prefix_expander = expandables.ExpanderWidget()
        add_prefix_expander.setDragDropMode(expandables.ExpanderDragDropModes.NoDragDrop)
        add_prefix_expander.setRolloutStyle(expandables.ExpanderStyles.Maya)
        manual_rename_layout.addWidget(add_prefix_expander)
        add_prefix_expander.addItem(title='ADD PREFIX', widget=add_prefix_widget, collapsed=False)

        add_prefix_lbl = QLabel('Prefix: ')
        self._add_prefix_line = QLineEdit()
        replace_lbl.setFixedWidth(55)

        reg_ex = QRegExp("[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._add_prefix_line)
        self._add_prefix_line.setValidator(text_validator)

        add_prefix_layout = QHBoxLayout()
        add_prefix_layout.setContentsMargins(4, 0, 4, 0)
        add_prefix_layout.setSpacing(2)
        add_prefix_layout.addWidget(add_prefix_lbl)
        add_prefix_layout.addWidget(self._add_prefix_line)
        add_prefix_widget.layout().addLayout(add_prefix_layout)

        add_prefix_widget.layout().addLayout(splitters.SplitterLayout())

        self._add_prefix_btn = QPushButton('Add')
        self._add_prefix_btn.setFixedHeight(20)
        self._add_prefix_btn.setFixedWidth(55)

        add_prefix_btn_layout = QHBoxLayout()
        add_prefix_btn_layout.setContentsMargins(4, 0, 4, 0)
        add_prefix_btn_layout.setSpacing(0)
        add_prefix_btn_layout.setAlignment(Qt.AlignRight)
        add_prefix_btn_layout.addWidget(self._add_prefix_btn)

        add_prefix_widget.layout().addLayout(add_prefix_btn_layout)


        ## Add Suffix Widget ###
        add_suffix_widget = QWidget()
        add_suffix_widget.setLayout(QVBoxLayout())
        add_suffix_widget.layout().setContentsMargins(0, 0, 0, 0)
        add_suffix_widget.layout().setSpacing(2)
        add_suffix_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        add_suffix_expander = expandables.ExpanderWidget()
        add_suffix_expander.setDragDropMode(expandables.ExpanderDragDropModes.NoDragDrop)
        add_suffix_expander.setRolloutStyle(expandables.ExpanderStyles.Maya)
        manual_rename_layout.addWidget(add_suffix_expander)
        add_suffix_expander.addItem(title='ADD SUFFIX', widget=add_suffix_widget, collapsed=False)


        add_suffix_lbl = QLabel('Sufix: ')
        self._add_suffix_line = QLineEdit()
        replace_lbl.setFixedWidth(55)

        reg_ex = QRegExp("[a-zA-Z_]+")
        text_validator = QRegExpValidator(reg_ex, self._add_suffix_line)
        self._add_suffix_line.setValidator(text_validator)

        add_suffix_layout = QHBoxLayout()
        add_suffix_layout.setContentsMargins(4, 0, 4, 0)
        add_suffix_layout.setSpacing(2)
        add_suffix_layout.addWidget(add_suffix_lbl)
        add_suffix_layout.addWidget(self._add_suffix_line)
        add_suffix_widget.layout().addLayout(add_suffix_layout)

        add_suffix_widget.layout().addLayout(splitters.SplitterLayout())

        self._add_suffix_btn = QPushButton('Add')
        self._add_suffix_btn.setFixedHeight(20)
        self._add_suffix_btn.setFixedWidth(55)

        add_suffix_btn_layout = QHBoxLayout()
        add_suffix_btn_layout.setContentsMargins(4, 0, 4, 0)
        add_suffix_btn_layout.setSpacing(0)
        add_suffix_btn_layout.setAlignment(Qt.AlignRight)
        add_suffix_btn_layout.addWidget(self._add_suffix_btn)

        add_suffix_widget.layout().addLayout(add_suffix_btn_layout)

        # ===============================================================================

        main_splitter = QSplitter(Qt.Horizontal)
        auto_rename_layout.addWidget(main_splitter)

        auto_widget = QWidget()
        auto_layout = QVBoxLayout()
        auto_widget.setLayout(auto_layout)
        main_splitter.addWidget(auto_widget)

        edit_icon = tpRenamer.resource.icon('edit', extension='png')
        self.edit_btn = button.IconButton(icon=edit_icon, icon_padding=2, button_style=button.ButtonStyles.FlatStyle)
        self.rules_list = QTreeWidget(self)
        self.rules_list.setHeaderHidden(True)
        self.rules_list.setSortingEnabled(True)
        self.rules_list.setRootIsDecorated(False)
        self.rules_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.rules_list.sortByColumn(0, Qt.AscendingOrder)
        self.rules_list.setUniformRowHeights(True)
        self.rules_list.setAlternatingRowColors(True)
        self.rules_list.setStyleSheet(
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

        auto_layout.addWidget(self.edit_btn)
        auto_layout.addWidget(self.rules_list)

        auto_w = QWidget()
        self.auto_l = QVBoxLayout()
        self.auto_l.setAlignment(Qt.AlignTop)
        auto_w.setLayout(self.auto_l)
        auto_w.setMinimumWidth(200)
        main_splitter.addWidget(auto_w)

        # ===============================================================================

        ## Extra Layout ###

        extra_layout = QHBoxLayout()
        extra_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addLayout(extra_layout)

        self._select_hierarchy_btn = QPushButton('Select Hierarchy')
        extra_layout.addWidget(self._select_hierarchy_btn)

    def setup_signals(self):

        self.rename_tab.currentChanged.connect(self._on_tab_changed)

        self._prefix_check.stateChanged.connect(self._prefix_line.setEnabled)
        self._suffix_check.stateChanged.connect(self._suffix_line.setEnabled)
        self._prefix_check.stateChanged.connect(self._update_example_rename)
        self._suffix_check.stateChanged.connect(self._update_example_rename)

        self._renamer_mult_method_combo.currentIndexChanged.connect(self._toggle_mult_naming_method)

        self._lower_radio.clicked.connect(self._update_example_rename)
        self._upper_radio.clicked.connect(self._update_example_rename)
        self._frame_pad_spin.valueChanged.connect(self._update_example_rename)

        self._none_side.toggled.connect(self._update_example_rename)
        self._right_side.toggled.connect(self._update_example_rename)
        self._center_side.toggled.connect(self._update_example_rename)
        self._mid_side.toggled.connect(self._update_example_rename)
        self._left_side.toggled.connect(self._update_example_rename)
        self._capital_side.toggled.connect(self._update_example_rename)

        self._renamer_line.textChanged.connect(self._update_example_rename)
        self._prefix_line.textChanged.connect(self._update_example_rename)
        self._suffix_line.textChanged.connect(self._update_example_rename)

        self._selected_radio.toggled.connect(self._update_hierarchy_cbx)
        self._all_radio.toggled.connect(self._update_hierarchy_cbx)

        self._add_prefix_btn.clicked.connect(self.add_prefix)
        self._add_suffix_btn.clicked.connect(self.add_suffix)
        self._select_hierarchy_btn.clicked.connect(self.select_hierarchy)

        self._renamer_btn.clicked.connect(self.rename_nodes)
        self._replace_btn.clicked.connect(self.replace_nodes)

        self.edit_btn.clicked.connect(self._on_open_naming_manager)
        self.rules_list.itemSelectionChanged.connect(self._on_change_name_rule)

        self._update_example_rename()

    def keyPressEvent(self, event):

        # Prevent lost focus when writing on QLineEdits
        if event.key() in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_CapsLock):
            event.accept()
        else:
            event.ignore()
    # endregion

    # region Public Functions
    def rename_nodes(self):
        """
        Method that renames selected nodes
        """

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            rename(maya.cmds.ls(sl=True), *self._get_rename_settings())
        else:
            raise NotImplementedError()

    def auto_rename_nodes(self, auto_name):
        """
        Method that auto rename selected nodes
        """

        if tp.Dcc.get_name() == tp.Dccs.Maya:
            rename(maya.cmds.ls(sl=True), text=auto_name, auto_rename=True)
        else:
            raise NotImplementedError()

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
    # endregion

    # region Private Functions
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

        jointEnd = self._last_joint_is_end_cbx.isChecked()

        return text, prefix, suffix, padding, naming_method, upper, side, jointEnd

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

    def _on_tab_changed(self, tab_index):

        if tab_index != 1 or not NAMING_IT_AVAILABLE:
            return

        self.rules_list.blockSignals(True)

        try:
            qtutils.clear_layout(self.auto_l)

            self.rules_list.clear()
            rules = nameit.NamingData.get_rules()

            item_to_select = None
            current_rule = nameit.NameIt.get_active_rule()

            for rule in rules:
                item = QTreeWidgetItem(self.rules_list, [rule.name])
                item.rule = rule
                self.rules_list.addTopLevelItem(item)
                self.rules_list.setCurrentItem(item)
                if current_rule and current_rule.name() == rule.name:
                    item_to_select = item
                self.rules_list.setItemSelected(item, False)
            if item_to_select:
                self.rules_list.setItemSelected(item_to_select, True)

            self.main_auto_layout = QFormLayout()
            self.auto_l.addLayout(self.main_auto_layout)

            self.auto_l.addLayout(splitters.SplitterLayout())
            rename_btn = QPushButton('Rename')
            rename_btn.clicked.connect(self._on_auto_rename)
            self.auto_l.addWidget(rename_btn)
        except Exception as e:
            self.rules_list.blockSignals(False)
            tpRenamer.logger.error(traceback.format_exc())

        self.rules_list.blockSignals(False)

        self._on_change_name_rule()

    def _on_change_name_rule(self):

        qtutils.clear_layout(self.main_auto_layout)

        rule_item = self.rules_list.currentItem()
        if not rule_item:
            return

        current_rule = nameit.NameIt.get_active_rule()
        nameit.NameIt.set_active_rule(name=rule_item.rule.name)
        rule_tokens = nameit.NamingData.get_tokens()

        active_tokens = list()
        active_rule = nameit.NameIt.get_active_rule()
        for field in active_rule.fields():
            for token in rule_tokens:
                if token.name == field:
                    active_tokens.append(token)

        self._token_widgets = OrderedDict()

        for token in reversed(active_tokens):
            token_name = token.name
            token_value = token.get_values_as_keyword()
            token_default = token.default

            if token_name == 'id':
                continue

            if token_value:
                w = QComboBox()
                w_l = QLabel()
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                w_l.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = [w, w_l]
                self.main_auto_layout.addRow(token_name, qtutils.get_line_layout('', self, w, QLabel(u'\u25ba'), w_l))
                for key, value in token_value.items():
                    if key == 'default':
                        continue
                    w.addItem(key)
                if token_default > 0:
                    w.setCurrentIndex(token_default-1)
            else:
                w = QLineEdit(self)
                w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self._token_widgets[token_name] = w
                self.main_auto_layout.addRow(token_name, qtutils.get_line_layout('', self, w))

        if current_rule:
            nameit.NameIt.set_active_rule(current_rule.name)

    def _on_open_naming_manager(self):
        if not NAMING_IT_AVAILABLE:
            return

        win = nameit.run()

        return win

    def _on_auto_rename(self):

        rule_item = self.rules_list.currentItem()
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
