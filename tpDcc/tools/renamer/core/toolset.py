#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains core implementation for Renamer Tool
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from tpDcc.managers import configs
from tpDcc.libs.qt.widgets import toolset
from tpDcc.libs.nameit.core import namelib

from tpDcc.tools.renamer.core import model, view, controller

LOGGER = logging.getLogger('tpDcc-tools-renamer')


class RenamerToolset(toolset.ToolsetWidget, object):

    def __init__(self, *args, **kwargs):

        self._naming_config = kwargs.get('naming_config', None)
        self._naming_lib = kwargs.get('naming_lib', None)
        self._naming_file = kwargs.get('naming_file', None)
        self._dev = kwargs.get('dev', False)

        super(RenamerToolset, self).__init__(*args, **kwargs)

    def contents(self):
        if not self._naming_config:
            self._naming_config = configs.get_config(
                config_name='tpDcc-naming', environment='development' if self._dev else 'production')

        naming_file = self._naming_file if self._naming_file and os.path.isfile(
            self._naming_file) else self._naming_config.get_path()
        naming_lib = self._naming_lib or namelib.NameLib(naming_file=naming_file)

        config = configs.get_config(config_name=self.ID, environment='development' if self._dev else 'production')
        renamer_model = model.RenamerModel(config=config, naming_config=self._naming_config)
        renamer_controller = controller.RenamerController(
            naming_lib=naming_lib, client=self.client, model=renamer_model)
        renamer_view = view.RenamerView(model=renamer_model, controller=renamer_controller, parent=self)

        return [renamer_view]
