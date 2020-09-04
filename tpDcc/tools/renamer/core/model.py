#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Renamer widget model class implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *

import tpDcc as tp
from tpDcc.libs.python import python

LOGGER = tp.LogsMgr().get_logger('tpDcc-tools-renamer')


class RenamerModel(QObject, object):

    selectionTypeChanged = Signal(int)
    filterTypeChanged = Signal(str)
    hierarchyCheckChanged = Signal(bool)
    renameShapeChanged = Signal(bool)
    globalAttributeChanged = Signal()
    rulesChanged = Signal(list)
    activeRuleChanged = Signal(object)
    tokensChanged = Signal(list)

    def __init__(self, config, names_config, naming_config):
        super(RenamerModel, self).__init__()

        self._config = config if config else tp.ToolsMgr().get_tool_config('tpDcc-tools-renamer')
        self._names_config = names_config if names_config else tp.ConfigsMgr().get_config(config_name='tpDcc-naming')
        self._naming_config = naming_config
        self._selection_type = 0
        self._hierarchy_check = False
        self._rename_shape = True
        self._filter_type = ''
        self._rules = list()
        self._active_rule = None
        self._tokens = list()

    @property
    def config(self):
        return self._config

    @property
    def names_config(self):
        return self._names_config

    @property
    def naming_config(self):
        return self._naming_config

    @property
    def selection_type(self):
        return self._selection_type

    @selection_type.setter
    def selection_type(self, value):
        self._selection_type = int(value)
        self.selectionTypeChanged.emit(self._selection_type)
        self.globalAttributeChanged.emit()

    @property
    def filter_type(self):
        return self._filter_type

    @filter_type.setter
    def filter_type(self, value):
        if isinstance(value, int):
            self._filter_type = self.node_types[value]
        else:
            self._filter_type = str(value)
        self.filterTypeChanged.emit(self._filter_type)
        self.globalAttributeChanged.emit()

    @property
    def hierarchy_check(self):
        return self._hierarchy_check

    @hierarchy_check.setter
    def hierarchy_check(self, flag):
        self._hierarchy_check = bool(flag)
        self.hierarchyCheckChanged.emit(self._hierarchy_check)
        self.globalAttributeChanged.emit()

    @property
    def rename_shape(self):
        return self._rename_shape

    @rename_shape.setter
    def rename_shape(self, flag):
        self._rename_shape = bool(flag)
        self.renameShapeChanged.emit(self._rename_shape)
        self.globalAttributeChanged.emit()

    @property
    def categories(self):
        if not self._config:
            LOGGER.warning(
                'Impossible to setup categories because tpDcc-tools-renamer configuration file is not available!')
            return list()

        categories = self._config.get('categories', default=list())
        if not categories:
            LOGGER.warning(
                'Impossible to setup categories because categories property is not defined in tpDcc-tools-renamer '
                'configuration file!')
            return categories

        return categories

    @property
    def nodes_to_discard(self):
        if not self._config:
            return list()

        discard_nodes = self._config.get('nodes_to_discard', default=list())

        return discard_nodes

    @property
    def types_to_discard(self):
        if not self._config:
            return list()

        types_to_discard = self._config.get('types_to_discard', default=list())

        return types_to_discard

    @property
    def node_types(self):
        return tp.Dcc.TYPE_FILTERS.keys()

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, rules_list):
        self._rules = python.force_list(rules_list)
        self.rulesChanged.emit(self._rules)

    @property
    def active_rule(self):
        return self._active_rule

    @active_rule.setter
    def active_rule(self, rule):
        if rule == self._active_rule:
            return

        self._active_rule = rule
        self.activeRuleChanged.emit(self._active_rule)

    @property
    def tokens(self):
        return self._tokens

    @tokens.setter
    def tokens(self, new_tokens):
        self._tokens = python.force_list(new_tokens)
        self.tokensChanged.emit(self._tokens)
