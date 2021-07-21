# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject
import camos.utils.pluginmanager as pluginmanager
from camos.gui.mainwindow import MainWindow

translate = QtWidgets.QApplication.translate


class camosApp(QObject):
    """[summary]

    Args:
        QObject ([type]): [description]
    """

    pluginsLoaded = pyqtSignal()

    def __init__(self):
        """[summary]
        """
        super(camosApp, self).__init__()
        self.setObjectName("camos")

        # Create the GUI with models
        self.gui = MainWindow(self)

        # App configuration
        # self.config = camosSettings.Config()
        # self.config.applyConfiguration(self.config.readConfiguration())

        # Load plugins
        self.plugins_mgr = pluginmanager.PluginManager()
        self.plugins_mgr.loadAllPlugins()
        self.plugins_mgr.loadDefaultPlotters()
        self.pluginsLoaded.emit()
