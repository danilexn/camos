# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5 import QtWidgets

import camos.utils.apptools as apptools
import camos.utils.pluginmanager as PluginManager

signal_types = {"timeseries":[3, "int"],
                "correlation":[2, "object"],
                "correlation_lag":[3, "object"],
                "summary":[2, "int"]}

class SignalViewModel(QObject):
    newdata = pyqtSignal()

    def __init__(self, data=[], parent=None):
        self.data = data
        self.parent = parent
        self.names = []
        self.sampling = []
        super(SignalViewModel, self).__init__()

    @pyqtSlot()
    def add_data(self, data, name = "New signal", _class = None, sampling = 10):
        self.data.append(data)
        if name in self.names or name == "":
            name = "New_{}_{}".format(name, len(self.names))
        self.names.append(name)
        self.sampling.append(sampling)
        self.newdata.emit()
        if _class != None:
            self.add_menu(_class, self.names[-1])

    def list_datasets(self, _type = None):
        if len(self.data) == 0:
            return None
        return self.names

    def add_menu(self, _class, name):
        gui = apptools.getApp().gui
        datasetsAct = QtWidgets.QAction("{}".format(name), gui)
        PluginManager.plugin_instances.append(_class)
        datasetsAct.triggered.connect(PluginManager.plugin_instances[-1].show)
        gui.datasetsMenu.addAction(datasetsAct)

    def __iter__(self):
        self._it = 0
        return self

    def __next__(self):
        if self._it < len(self.data):
            _it = self._it
            self._it += 1
            return self.names[_it], self.data[_it]
        else:
            raise StopIteration