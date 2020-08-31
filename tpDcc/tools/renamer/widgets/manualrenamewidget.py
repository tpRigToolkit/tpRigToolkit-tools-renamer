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
from tpDcc.libs.qt.widgets import accordion, dividers

from tpDcc.tools.renamer.widgets import renamerwidget, replacerwidget, prefixsuffixwidget, numbersidewidget
from tpDcc.tools.renamer.widgets import namespacewidget, utilswidget


class ManualRenameWidget(base.BaseWidget, object):

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
        self._utils_widget.doAutoSuffix.connect(self.doAutoSuffix.emit)
        self._utils_widget.doUniqueName.connect(self.doUniqueName.emit)
        self._utils_widget.doRemoveAllNumbers.connect(self.doRemoveAllNumbers.emit)
        self._utils_widget.doRemoveTailNumbers.connect(self.doRemoveTailNumbers.emit)
        self._rename_btn.clicked.connect(self.doRename.emit)

        if tpDcc.is_maya():
            self._namespace_widget.doAddNamespace.connect(self.doAddNamespace.emit)
            self._namespace_widget.doRemoveNamespace.connect(self.doRemoveNamespace.emit)

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
