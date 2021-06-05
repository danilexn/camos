#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import logging
import traceback
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

from camos.tasks.analysis import Analysis
from camos.tasks.processing import Processing
from camos.tasks.saving import Saving
from camos.tasks.opening import Opening
import camos.utils.apptools as apptools

PLUGIN_GROUP = "camos.plugins"

log = logging.getLogger(__name__)


def _create_instance(plugin_class):
    instance = None
    try:
        gui = apptools.getApp().gui
        model = gui.model
        signalmodel = gui.signalmodel
        instance = plugin_class(model=model, parent=gui)
    except Exception as e:
        log.error("Failed to create plugin instance")
        log.error(e)
        log.info(traceback.format_exc())
    return instance


class PluginManager(object):
    def __init__(self, enabled_plugins=None):
        self.enabled_plugins = enabled_plugins
        self.all_plugins = {}
        self.loaded_plugins = {}

    def _disable_not_loaded(self):
        self.enabled_plugins = list(self.loaded_plugins.keys())

    def loadAll(self):
        self.loaded_plugins = {}
        package_dir = Path(__file__).resolve().parent.parent.joinpath("plugins")
        for (_, module_name, _) in iter_modules([package_dir]):
            # import the module and iterate through its attributes
            module = import_module(f"camos.plugins.{module_name}.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isclass(attribute):
                    # Add the class to this package's variables
                    if any(
                        item in attribute.__bases__
                        for item in [Analysis, Processing, Saving, Opening]
                    ):
                        self.loaded_plugins[attribute_name] = _create_instance(
                            attribute
                        )

        self._disable_not_loaded()
