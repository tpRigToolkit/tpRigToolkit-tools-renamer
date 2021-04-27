#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains number renamer plugin implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import QObject

from tpDcc.managers import resources

from tpDcc.tools.renamer.core import plugin


class NumberRenamerPlugin(plugin.RenamerPlugin):

    VERSION = '0.0.1'
    ID = 'number'

    PLUGIN_HEIGHT = 100

    def __init__(self, model, controller, parent=None):
        super(NumberRenamerPlugin, self).__init__(model=model, controller=controller, parent=parent)

    @classmethod
    def create(cls, parent):
        model = NumberRenamerPluginModel()
        controller = NumberRenamerPluginController(model=model)
        return cls(model=model, controller=controller, parent=parent)

    @classmethod
    def get_title(cls):
        return 'Number'

    @classmethod
    def get_icon(cls):
        return resources.icon('number')


class NumberRenamerPluginModel(QObject):
    def __init__(self):
        super(NumberRenamerPluginModel, self).__init__()


class NumberRenamerPluginController(object):
    def __init__(self, model):
        super(NumberRenamerPluginController, self).__init__()

        self._model = model

    @property
    def model(self):
        return self._model
