#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains manual rename widgets for tpRenamer
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import accordion, splitters

from tpDcc.tools.renamer.widgets import renamerwidget, replacerwidget, prefixsuffixwidget, numbersidewidget
from tpDcc.tools.renamer.widgets import namespacewidget, utilswidget


class ManualRenameWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    replaceUpdate = Signal()
    doName = Signal(str)
    doSearchReplace = Signal(str, str)
    doAddPrefix = Signal(str)
    doRemovePrefix = Signal()
    doAddSuffix = Signal(str)
    doRemoveSuffix = Signal()
    doRemoveFirst = Signal(int)
    doRemoveLast = Signal(int)
    doReplacePadding = Signal(int)
    doAppendPadding = Signal(int)
    doChangePadding = Signal(int)
    doSide = Signal(str)
    doAddNamespace = Signal(str)
    doRemoveNamespace = Signal(str)
    doAutoSuffix = Signal()
    doUniqueName = Signal()
    doRemoveAllNumbers = Signal()
    doRemoveTailNumbers = Signal()
    doRename = Signal()
    
    def __init__(self, parent=None):
        super(ManualRenameWidget, self).__init__(parent=parent)

    def ui(self):
        super(ManualRenameWidget, self).ui()

        manual_accordion = accordion.AccordionWidget()
        self.main_layout.addWidget(manual_accordion)

        self._renamer_widget = renamerwidget.RenamerWidget()
        self._prefix_suffix_widget = prefixsuffixwidget.PrefixSuffixWidget()
        self._number_side_widget = numbersidewidget.NumberSideWidget()
        self._namespace_widget = None
        if tpDcc.is_maya():
            self._namespace_widget = namespacewidget.NamespaceWidget()
        self._replacer_widget = replacerwidget.ReplacerWidget()
        self._utils_widget = utilswidget.UtilsWidget()

        manual_accordion.add_item('Name', self._renamer_widget)
        manual_accordion.add_item('Prefix/Suffix', self._prefix_suffix_widget)
        manual_accordion.add_item('Number & Side', self._number_side_widget)
        if self._namespace_widget:
            manual_accordion.add_item('Namespace', self._namespace_widget)
        manual_accordion.add_item('Search & Replace', self._replacer_widget)
        manual_accordion.add_item('Utils', self._utils_widget)

        self._rename_btn = QPushButton('Rename')
        self._rename_btn.setIcon(tpDcc.ResourcesMgr().icon('rename'))
        self.main_layout.addLayout(splitters.SplitterLayout())
        self.main_layout.addWidget(self._rename_btn)

    def setup_signals(self):
        self._renamer_widget.renameUpdate.connect(self.renameUpdate.emit)
        self._renamer_widget.doName.connect(self.doName.emit)
        self._prefix_suffix_widget.renameUpdate.connect(self.renameUpdate.emit)
        self._number_side_widget.renameUpdate.connect(self.renameUpdate.emit)
        if self._namespace_widget:
            self._namespace_widget.renameUpdate.connect(self.renameUpdate.emit)
        self._replacer_widget.replaceUpdate.connect(self.replaceUpdate.emit)
        self._replacer_widget.doSearchReplace.connect(self.doSearchReplace.emit)
        self._prefix_suffix_widget.doAddPrefix.connect(self.doAddPrefix.emit)
        self._prefix_suffix_widget.doAddSuffix.connect(self.doAddSuffix.emit)
        self._prefix_suffix_widget.doRemovePrefix.connect(self.doRemovePrefix.emit)
        self._prefix_suffix_widget.doRemoveSuffix.connect(self.doRemoveSuffix.emit)
        self._prefix_suffix_widget.doRemoveFirst.connect(self.doRemoveFirst.emit)
        self._prefix_suffix_widget.doRemoveLast.connect(self.doRemoveLast.emit)
        self._number_side_widget.doReplacePadding.connect(self.doReplacePadding.emit)
        self._number_side_widget.doAppendPadding.connect(self.doAppendPadding.emit)
        self._number_side_widget.doChangePadding.connect(self.doChangePadding.emit)
        self._number_side_widget.doSide.connect(self.doSide.emit)
        self._namespace_widget.doAddNamespace.connect(self.doAddNamespace.emit)
        self._namespace_widget.doRemoveNamespace.connect(self.doRemoveNamespace.emit)
        self._utils_widget.doAutoSuffix.connect(self.doAutoSuffix.emit)
        self._utils_widget.doUniqueName.connect(self.doUniqueName.emit)
        self._utils_widget.doRemoveAllNumbers.connect(self.doRemoveAllNumbers.emit)
        self._utils_widget.doRemoveTailNumbers.connect(self.doRemoveTailNumbers.emit)
        self._rename_btn.clicked.connect(self.doRename.emit)

    def get_rename_settings(self):
        """
        Function that returns current rename settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        text = self._renamer_widget.get_rename_settings()
        prefix, suffix, remove_first, remove_last, joint_end = self._prefix_suffix_widget.get_rename_settings()
        padding, naming_method, upper, side = self._number_side_widget.get_rename_settings()

        return (
            text, prefix, suffix, padding, naming_method,
            upper, side, remove_first, remove_last, joint_end
        )

    def get_replace_settings(self):
        """
        Function that returns current replace settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        return self._replacer_widget.get_replace_settings()

