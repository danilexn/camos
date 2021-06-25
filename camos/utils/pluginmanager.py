# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import logging
import traceback
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

from PyQt5 import QtWidgets

from camos.tasks.analysis import Analysis
from camos.tasks.processing import Processing
from camos.tasks.saving import Saving
from camos.tasks.opening import Opening
import camos.utils.apptools as apptools

PLUGIN_GROUP = "camos.plugins"

log = logging.getLogger(__name__)


def _create_instance(plugin_class, attribute_name, base):
    instance = None
    try:
        gui = apptools.getApp().gui
        analysisAct = QtWidgets.QAction("{}".format(plugin_class.analysis_name), gui)
        analysisAct.triggered.connect(lambda: make_instance(plugin_class))
        if Analysis in base:
            gui.analysisMenu.addAction(analysisAct)
        elif Processing in base:
            gui.processMenu.addAction(analysisAct)
        elif Saving in base:
            gui.saveMenu.addAction(analysisAct)
        elif Opening in base:
            gui.openMenu.addAction(analysisAct)
        # instance = plugin_class(model=model, parent=gui, signal = signalmodel)
    except Exception as e:
        log.error("Failed to create plugin instance")
        log.error(e)
        log.info(traceback.format_exc())
    return instance


def make_instance(_class):
    gui = apptools.getApp().gui
    model = gui.model
    signalmodel = gui.signalmodel
    instance = _class(model=model, parent=gui, signal=signalmodel)
    instance.display()


class PluginManager(object):
    def __init__(self, enabled_plugins=None):
        self.enabled_plugins = enabled_plugins
        self.all_plugins = {}
        self.loaded_plugins = {}

    def _disable_not_loaded(self):
        self.enabled_plugins = list(self.loaded_plugins.keys())

    def loadAll(self):
        self.loaded_plugins = {}
        package_dir = (
            Path(__file__).resolve().parent.parent.joinpath("plugins")
        )
        for (_, module_name, _) in iter_modules([package_dir]):
            # import the module and iterate through its attributes
            module = import_module(
                f"camos.plugins.{module_name}.{module_name}"
            )
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isclass(attribute):
                    # Add the class to this package's variables
                    if any(
                        item in attribute.__bases__
                        for item in [Analysis, Processing, Saving, Opening]
                    ):
                        self.loaded_plugins[attribute_name] = _create_instance(
                            attribute, attribute_name, attribute.__bases__
                        )

        self._disable_not_loaded()
