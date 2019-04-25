#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRenamer
"""

from __future__ import print_function, division, absolute_import

import os
import sys

from tpPyUtils import logger as logger_utils
from tpQtLib.core import resource as resource_utils

# =================================================================================

logger = None
resource = None

# =================================================================================


class tpRenamerResource(resource_utils.Resource, object):
    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class tpRenamer(object):
    def __init__(self):
        super(tpRenamer, self).__init__()

    @classmethod
    def initialize(cls, do_reload=False):
        cls.create_logger()
        cls.register_resource()

        if do_reload:
            cls.reload_all()

    @staticmethod
    def create_logger():
        """
        Creates and initializes tpRenamer logger
        """

        global logger
        logger = logger_utils.Logger(name=tpRenamer.__name__, level=logger_utils.LoggerLevel.DEBUG).logger
        logger.debug('Initializing tpRenamer Logger ...')
        return logger

    @staticmethod
    def register_resource():
        """
        Register resource class used to load tpRenamer resources
        """

        global resource
        resource = tpRenamerResource

    @staticmethod
    def reload_all():
        # if os.environ.get('SOLSTICE_DEV_MODE', '0') == '1':
        import inspect
        scripts_dir = os.path.dirname(__file__)
        for key, module in sys.modules.items():
            try:
                module_path = inspect.getfile(module)
            except TypeError:
                continue
            if module_path == __file__:
                continue
            if module_path.startswith(scripts_dir):
                reload(module)


def run(do_reload=False):
    tpRenamer.initialize(do_reload=do_reload)
    from tpRenamer import renamer
    win = renamer.run()
    return win
