#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that manages utils rename functionality
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import splitters

if tpDcc.is_maya():
    from tpDcc.dccs.maya.core import gui, namespace


class UtilsWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    doAutoSuffix = Signal()
    doUniqueName = Signal()
    doRemoveAllNumbers = Signal()
    doRemoveTailNumbers = Signal()

    def __init__(self, parent=None):
        super(UtilsWidget, self).__init__(parent=parent)

    def ui(self):
        super(UtilsWidget, self).ui()

        base_layout = QVBoxLayout()
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(2)
        self.main_layout.addLayout(base_layout)

        name_utils_layout = QHBoxLayout()
        name_utils_layout.setContentsMargins(0, 0, 0, 0)
        name_utils_layout.setSpacing(5)
        self._automatic_suffix_btn = QPushButton('Automatic Suffix')
        self._automatic_suffix_btn.setIcon(tpDcc.ResourcesMgr().icon('suffix'))
        self._make_unique_name_btn = QPushButton('Make Unique Name')
        self._make_unique_name_btn.setIcon(tpDcc.ResourcesMgr().icon('name'))
        name_utils_layout.addWidget(self._automatic_suffix_btn)
        name_utils_layout.addWidget(self._make_unique_name_btn)

        if tpDcc.is_maya():
            namespace_utils_layout = QHBoxLayout()
            namespace_utils_layout.setContentsMargins(0, 0, 0, 0)
            namespace_utils_layout.setSpacing(5)
            self._clean_unused_namespaces_btn = QPushButton('Unused Namespaces')
            self._clean_unused_namespaces_btn.setIcon(tpDcc.ResourcesMgr().icon('clean'))
            self._namespace_editor_btn = QPushButton('Namespace Editor')
            self._namespace_editor_btn.setIcon(tpDcc.ResourcesMgr().icon('browse_page'))
            self._reference_editor_btn = QPushButton('Reference Editor')
            self._reference_editor_btn.setIcon(tpDcc.ResourcesMgr().icon('connect'))
            namespace_utils_layout.addWidget(self._clean_unused_namespaces_btn)
            namespace_utils_layout.addWidget(self._namespace_editor_btn)
            namespace_utils_layout.addWidget(self._reference_editor_btn)

        index_utils_layout = QHBoxLayout()
        index_utils_layout.setContentsMargins(0, 0, 0, 0)
        index_utils_layout.setSpacing(5)
        self._remove_all_numbers_btn = QPushButton('Remove All Numbers')
        self._remove_all_numbers_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        self._remove_tail_numbers_btn = QPushButton('Remove Tail Numbers')
        self._remove_tail_numbers_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        index_utils_layout.addWidget(self._remove_all_numbers_btn)
        index_utils_layout.addWidget(self._remove_tail_numbers_btn)

        base_layout.addLayout(name_utils_layout)
        base_layout.addLayout(splitters.SplitterLayout())
        base_layout.addLayout(index_utils_layout)
        if tpDcc.is_maya():
            base_layout.addLayout(splitters.SplitterLayout())
            base_layout.addLayout(namespace_utils_layout)

    def setup_signals(self):
        self._automatic_suffix_btn.clicked.connect(self._on_auto_rename_suffix)
        self._make_unique_name_btn.clicked.connect(self._on_unique_name)
        self._remove_all_numbers_btn.clicked.connect(self._on_remove_all_numbers)
        self._remove_tail_numbers_btn.clicked.connect(self._on_remove_tail_numbers)
        if tpDcc.is_maya():
            self._clean_unused_namespaces_btn.clicked.connect(self._on_remove_unused_namespaces)
            self._namespace_editor_btn.clicked.connect(self._on_open_namespace_editor)
            self._reference_editor_btn.clicked.connect(self._on_open_reference_editor)

    def _on_auto_rename_suffix(self):
        self.doAutoSuffix.emit()

    def _on_unique_name(self):
        self.doUniqueName.emit()

    def _on_remove_all_numbers(self):
        self.doRemoveAllNumbers.emit()

    def _on_remove_tail_numbers(self):
        self.doRemoveTailNumbers.emit()

    def _on_open_namespace_editor(self):
        if not tpDcc.is_maya():
            return

        gui.open_namespace_editor()

    def _on_open_reference_editor(self):
        if not tpDcc.is_maya():
            return

        gui.open_reference_editor()

    def _on_remove_unused_namespaces(self):
        if not tpDcc.is_maya():
            return

        namespace.remove_empty_namespaces()