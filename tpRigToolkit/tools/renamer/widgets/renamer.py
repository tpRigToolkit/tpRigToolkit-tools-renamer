#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tool that allow to rename DCC nodes in an easy way
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from tpRigToolkit.libs.naming.core import naminglib

import tpDcc
from tpDcc.tools.renamer.widgets import renamer


class RigToolkitRenamerWidget(renamer.RenamerWidget, object):

    NAMING_LIB = naminglib.RigToolkitNameLib

    def __init__(self, config=None, parent=None):

        naming_config = tpDcc.ConfigsMgr().get_config(config_name='tpDcc-naming', environment='development')
        super(RigToolkitRenamerWidget, self).__init__(config=config, naming_config=naming_config, parent=parent)
