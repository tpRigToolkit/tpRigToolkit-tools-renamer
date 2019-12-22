#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Widget that contains manual rename widgets for tpRenamer
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *

from tpQtLib.core import base

from tpRenamer.widgets import renamerwidget, replacerwidget


class ManualRenameWidget(base.BaseWidget, object):

    renameUpdate = Signal()
    replaceUpdate = Signal()

    def __init__(self, parent=None):
        super(ManualRenameWidget, self).__init__(parent=parent)

    def ui(self):
        super(ManualRenameWidget, self).ui()

        self._renamer_widget = renamerwidget.RenamerWidget()
        self._replacer_widget = replacerwidget.ReplacerWidget()

        self.main_layout.addWidget(self._renamer_widget)
        self.main_layout.addWidget(self._replacer_widget)

        # extra_layout = QHBoxLayout()
        # extra_layout.setContentsMargins(10, 10, 10, 10)
        # self.main_layout.addLayout(extra_layout)
        #
        # self._select_hierarchy_btn = QPushButton('Select Hierarchy')
        # extra_layout.addWidget(self._select_hierarchy_btn)

    def setup_signals(self):
        self._renamer_widget.renameUpdate.connect(self.renameUpdate.emit)
        self._replacer_widget.replaceUpdate.connect(self.replaceUpdate.emit)

    def get_rename_settings(self):
        """
        Function that returns current rename settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        return self._renamer_widget.get_rename_settings()

    def get_replace_settings(self):
        """
        Function that returns current replace settings
        :return: str, str, str, int, bool, bool, str, bool
        """

        return self._replacer_widget.get_replace_settings()
