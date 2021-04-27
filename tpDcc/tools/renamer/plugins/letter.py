#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains letter renamer plugin implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import QObject
from Qt.QtWidgets import QWidget

from tpDcc.managers import resources
from tpDcc.libs.qt.widgets import layouts, buttons, label, switch

from tpDcc.tools.renamer.core import plugin


class LetterRenamerPlugin(plugin.RenamerPlugin):

    VERSION = '0.0.1'
    ID = 'letter'

    PLUGIN_HEIGHT = 130

    def __init__(self, model, controller, parent=None):
        super(LetterRenamerPlugin, self).__init__(model=model, controller=controller, parent=parent)

    @classmethod
    def create(cls, parent):
        model = LetterRenamerPluginModel()
        controller = LetterRenamerPluginController(model=model)
        return cls(model=model, controller=controller, parent=parent)

    @classmethod
    def get_title(cls):
        return 'Letter'

    @classmethod
    def get_icon(cls):
        return resources.icon('letter')

    def get_custom_widget(self):
        widget = QWidget(parent=self)
        widget_layout = layouts.VerticalLayout(spacing=0, margins=(2, 2, 2, 2))
        widget.setLayout(widget_layout)

        letters_layout = layouts.GridLayout(spacing=2, margins=(0, 0, 0, 0))
        i = 0
        j = 0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if i % 14 == 0:
                j += i
                i = 0
            letter_button = buttons.StyleBaseButton(letter, button_style=buttons.ButtonStyles.FlatStyle, parent=self)
            letter_button.setCheckable(True)
            letters_layout.addWidget(letter_button, j, i)
            if i == 0 and j == 0:
                letter_button.setChecked(True)
            i += 1
        widget_layout.addLayout(letters_layout)

        capital_widget = QWidget(parent=self)
        capital_layout = layouts.HorizontalLayout()
        capital_widget.setLayout(capital_layout)
        capital_label = label.BaseLabel('Capital:', parent=self)
        self._capital_switch = switch.SwitchWidget(parent=self)
        self._capital_switch.setChecked(True)
        capital_layout.addStretch()
        capital_layout.addWidget(capital_label)
        capital_layout.addWidget(self._capital_switch)
        capital_layout.addStretch()
        letters_layout.addWidget(capital_widget, j, i+1, 1, 2)

        return widget


class LetterRenamerPluginModel(QObject):
    def __init__(self):
        super(LetterRenamerPluginModel, self).__init__()


class LetterRenamerPluginController(object):
    def __init__(self, model):
        super(LetterRenamerPluginController, self).__init__()

        self._model = model

    @property
    def model(self):
        return self._model
