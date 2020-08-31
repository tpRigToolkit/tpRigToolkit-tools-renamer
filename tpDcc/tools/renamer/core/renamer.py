#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains core implementation for Renamer Tool
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import importlib

import tpDcc as tp
from tpDcc.core import tool
from tpDcc.libs.qt.widgets import toolset
from tpDcc.tools.renamer.core import renamerclient

# Defines ID of the tool
TOOL_ID = 'tpDcc-tools-renamer'


class RenamerTool(tool.DccTool, object):
    def __init__(self, *args, **kwargs):
        super(RenamerTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Renamer',
            'id': TOOL_ID,
            'supported_dccs': {'maya': ['2017', '2018', '2019', '2020']},
            'logo': 'renamer',
            'icon': 'renamer',
            'tooltip': 'Renamer Tool to easily rename DCC objects in a visual way',
            'tags': ['tpDcc', 'dcc', 'tool', 'renamer'],
            'logger_dir': os.path.join(os.path.expanduser('~'), 'tpDcc', 'logs', 'tools'),
            'logger_level': 'INFO',
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


class RenamerToolsetWidget(toolset.ToolsetWidget, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):

        self._naming_config = kwargs.get('naming_config', None)
        self._naming_lib = kwargs.get('naming_lib', None)
        self._dev = kwargs.get('dev', False)

        if not self._naming_config:
            self._naming_config = tp.ConfigsMgr().get_config(
                config_name='tpDcc-naming', environment='development' if self._dev else 'production')

        super(RenamerToolsetWidget, self).__init__(*args, **kwargs)

    def setup_client(self):

        self._client = renamerclient.RenamerClient()
        self._client.signals.dccDisconnected.connect(self._on_dcc_disconnected)

        if not tp.is_standalone():
            dcc_mod_name = '{}.dccs.{}.renamerserver'.format(TOOL_ID.replace('-', '.'), tp.Dcc.get_name())
            try:
                mod = importlib.import_module(dcc_mod_name)
                if hasattr(mod, 'RenamerServer'):
                    server = mod.RenamerServer(self, client=self._client, update_paths=False)
                    self._client.set_server(server)
                    self._update_client()
            except Exception as exc:
                tp.logger.warning(
                    'Impossible to launch ControlRig server! Error while importing: {} >> {}'.format(dcc_mod_name, exc))
                return
        else:
            self._update_client()

    def contents(self):

        from tpDcc.tools.renamer.core import model, view, controller

        renamer_model = model.RenamerModel(
            config=self.CONFIG, naming_config=self._naming_config, naming_lib=self._naming_lib)
        renamer_controller = controller.RenamerController(client=self._client, model=renamer_model)
        renamer_view = view.RenamerView(
            model=renamer_model, controller=renamer_controller, parent=self)

        return [renamer_view]


if __name__ == '__main__':
    import tpDcc
    import tpDcc.loader

    tpDcc.loader.init(dev=False)

    tpDcc.ToolsMgr().launch_tool_by_id('tpDcc-tools-renamer')
