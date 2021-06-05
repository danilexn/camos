# coding=utf-8
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
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
import camos.utils.pluginmanager as pluginmanager
from camos.gui.mainwindow import MainWindow
import camos.utils.settings as camosSettings

translate = QtWidgets.QApplication.translate


class camosApp(QObject):
    pluginsLoaded = pyqtSignal()

    def __init__(self):
        super(camosApp, self).__init__()
        self.setObjectName("VTApp")

        # Create the GUI with models
        self.gui = MainWindow(self)

        # App configuration
        # self.config = camosSettings.Config()
        # self.config.applyConfiguration(self.config.readConfiguration())

        # Load plugins
        self.plugins_mgr = pluginmanager.PluginManager()
        self.plugins_mgr.loadAll()
        self.pluginsLoaded.emit()
