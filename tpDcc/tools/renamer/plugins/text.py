#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains text renamer plugin implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import QObject

from tpDcc.managers import resources
from tpDcc.libs.qt.widgets import lineedit

from tpDcc.tools.renamer.core import plugin


class TextRenamerPlugin(plugin.RenamerPlugin):

    VERSION = '0.0.1'
    ID = 'text'

    PLUGIN_HEIGHT = 100

    def __init__(self, model, controller, parent=None):
        super(TextRenamerPlugin, self).__init__(model=model, controller=controller, parent=parent)

    @classmethod
    def get_title(cls):
        return 'Text'

    @classmethod
    def get_icon(cls):
        return resources.icon('text')

    @classmethod
    def create(cls, parent):
        model = TextRenamerPluginModel()
        controller = TextRenamerPluginController(model=model)
        return cls(model=model, controller=controller, parent=parent)

    def get_custom_widget(self):
        self._line_edit = lineedit.BaseLineEdit(parent=self)
        frame_bg_color = self.palette().color(self.backgroundRole()).darker(225)
        self._line_edit.setStyleSheet(
            'border-radius: 5px; background-color: rgb({}, {}, {}, 100);'.format(
                frame_bg_color.redF() * 255, frame_bg_color.greenF() * 255, frame_bg_color.blueF() * 255))

        return self._line_edit


class TextRenamerPluginModel(QObject):
    def __init__(self):
        super(TextRenamerPluginModel, self).__init__()


class TextRenamerPluginController(object):
    def __init__(self, model):
        super(TextRenamerPluginController, self).__init__()

        self._model = model

    @property
    def model(self):
        return self._model
