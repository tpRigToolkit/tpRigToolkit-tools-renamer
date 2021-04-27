#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains node type renamer plugin implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import QObject

from tpDcc.managers import resources

from tpDcc.tools.renamer.core import plugin


class NodeTypeRenamerPlugin(plugin.RenamerPlugin):

    VERSION = '0.0.1'
    ID = 'nodetype'

    PLUGIN_HEIGHT = 80

    def __init__(self, model, controller, parent=None):
        super(NodeTypeRenamerPlugin, self).__init__(model=model, controller=controller, parent=parent)

    @classmethod
    def create(cls, parent):
        model = NodeTypeRenamerPluginModel()
        controller = NodeTypeRenamerPluginController(model=model)
        return cls(model=model, controller=controller, parent=parent)

    @classmethod
    def get_title(cls):
        return 'Node Type'

    @classmethod
    def get_icon(cls):
        return resources.icon('puzzle')


class NodeTypeRenamerPluginModel(QObject):
    def __init__(self):
        super(NodeTypeRenamerPluginModel, self).__init__()


class NodeTypeRenamerPluginController(object):
    def __init__(self, model):
        super(NodeTypeRenamerPluginController, self).__init__()

        self._model = model

    @property
    def model(self):
        return self._model
