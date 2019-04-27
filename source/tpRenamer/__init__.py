#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRenamer
"""

from __future__ import print_function, division, absolute_import

import os
import inspect

from tpPyUtils import importer
from tpQtLib.core import resource as resource_utils

# =================================================================================

logger = None
resource = None

# =================================================================================


class tpRenamerResource(resource_utils.Resource, object):
    RESOURCES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources')


class tpRenamer(importer.Importer, object):
    def __init__(self):
        super(tpRenamer, self).__init__(module_name='tpRenamer')

    def get_module_path(self):
        """
        Returns path where tpRenamer module is stored
        :return: str
        """

        try:
            mod_dir = os.path.dirname(inspect.getframeinfo(inspect.currentframe()).filename)
        except Exception:
            try:
                mod_dir = os.path.dirname(__file__)
            except Exception:
                try:
                    import tpDccLib
                    mod_dir = tpDccLib.__path__[0]
                except Exception:
                    return None

        return mod_dir


def init(do_reload=False):
    """
    Initializes module
    :param do_reload: bool, Whether to reload modules or not
    """

    tprenamer_importer = importer.init_importer(importer_class=tpRenamer, do_reload=do_reload)

    global logger
    global resource
    logger = tprenamer_importer.logger
    resource = tpRenamerResource

    tprenamer_importer.import_modules()
    tprenamer_importer.import_packages(only_packages=True)



def run(do_reload=False):
    init(do_reload=do_reload)
    from tpRenamer import renamer
    win = renamer.run()
    return win
