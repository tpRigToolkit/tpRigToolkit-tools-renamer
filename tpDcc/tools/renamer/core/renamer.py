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

from tpDcc.core import tool
from tpDcc.libs.qt.widgets import toolset

# Defines ID of the tool
TOOL_ID = 'tpDcc-tools-renamer'

# We skip the reloading of this module when launching the tool
no_reload = True


class RenamerTool(tool.DccTool, object):
    def __init__(self, manager, config, settings):
        super(RenamerTool, self).__init__(manager=manager, config=config, settings=settings)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Renamer',
            'id': 'tpDcc-tools-renamer',
            'icon': 'renamer',
            'tooltip': 'Renamer Tool to easily rename DCC objects in a visual way',
            'tags': ['tpDcc', 'dcc', 'tool', 'renamer'],
            'is_checkable': False,
            'is_checked': False,
            'menu_ui': {'label': 'Renamer', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'menu': [{'type': 'menu', 'children': [{'id': 'tpDcc-tools-renamer', 'type': 'tool'}]}],
            'shelf': [
                {'name': 'tpDcc', 'children': [{'id': 'tpDcc-tools-renamer', 'display_label': False, 'type': 'tool'}]}
            ]
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


class RenamerToolsetWidget(toolset.ToolsetWidget, object):
    ID = TOOL_ID

    def __init__(self, *args, **kwargs):
        super(RenamerToolsetWidget, self).__init__(*args, **kwargs)

    def contents(self):

        from tpDcc.tools.renamer.widgets import renamer

        return [renamer.RenamerWidget()]

