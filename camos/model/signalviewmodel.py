# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
import copy

import camos.utils.apptools as apptools
import camos.utils.pluginmanager as PluginManager
from camos.viewport.signalviewer import SignalViewer

signal_types = {
    "timeseries": [3, "int"],
    "correlation": [2, "object"],
    "correlation_lag": [3, "object"],
    "summary": [2, "int"],
}

MAXNAMELEN = 30


class SignalViewModel(QObject):
    newdata = pyqtSignal()

    def __init__(self, data=[], parent=None):
        self.data = data
        self.parent = parent
        self.names = []
        self.sampling = []
        self.masks = []
        self.viewers = []
        super(SignalViewModel, self).__init__()

    @pyqtSlot()
    def add_data(self, data, name="New signal", _class=None, sampling=10, mask=[]):
        self.data.append(data)
        if name in self.names or name == "":
            name = "New_{}_{}".format(name, len(self.names))

        if len(name) > MAXNAMELEN:
            name = name[0:MAXNAMELEN]

        self.names.append(name)
        self.sampling.append(sampling)
        self.masks.append(mask)
        self.newdata.emit()
        self.add_viewer(_class, self.names[-1])

    def list_datasets(self, _type=None):
        if len(self.data) == 0:
            return None
        return self.names

    def data_remove(self, index):
        """Given an index, removes the data object and properties from their lists

        Args:
            index (int): position of the data track in the self.data list
        """
        assert index != None
        self.data.pop(index)
        self.names.pop(index)
        self.sampling.pop(index)
        self.masks.pop(index)
        self.viewers.pop(index)

    def add_viewer(self, _class, name):
        if _class != None:
            gui = apptools.getApp().gui
            PluginManager.plugin_instances.append(_class)
            gui.container.add_data_layer(name)
            self.viewers.append(PluginManager.plugin_instances[-1].show)
        else:
            self.viewers.append([])

    def filter_data(self, index, IDs):
        assert "CellID" in self.data[index].dtype.names

        _filtered_idx = np.isin(self.data[index][:]["CellID"], IDs)
        _filtered = self.data[index][_filtered_idx]

        _sv = SignalViewer(self.parent, _filtered)
        _sv.display()

        self.add_data(
            _filtered,
            name=self.names[index],
            _class=_sv,
            sampling=self.sampling[index],
        )

    def duplicate_data(self, index=0):
        """Duplicates the current data

        Args:
            index (int, optional): index of the data to duplicate, according to self.data. Defaults to 0.
        """
        data = copy.deepcopy(self.data[index])
        _sv = SignalViewer(self.parent, data)
        _sv.display()
        self.add_data(
            data,
            name="Duplicate of {}".format(self.names[index]),
            _class=_sv,
            sampling=self.sampling[index],
        )

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
