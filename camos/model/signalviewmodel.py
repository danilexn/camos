# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Thu Jul 15 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.plotter.signal import Signal
from camos.plotter.image import Image
from camos.plotter.raster import Raster
from camos.plotter.event import Event
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
import copy

import camos.utils.apptools as apptools
import camos.utils.pluginmanager as PluginManager
from camos.viewport.signalviewer2 import SignalViewer2

MAXNAMELEN = 300


def choose_plotter(data):
    mask_plots = ["MFR", "ISI", "Nearest"]
    if data.dtype.names == None:
        return Signal, None
    elif data.dtype.names[1] == "Burst":
        return Event, data.dtype.names[1]
    elif data.dtype.names[1] == "Active":
        return Raster, data.dtype.names[1]
    elif data.dtype.names[1] in mask_plots:
        return Image, data.dtype.names[1]
    else:
        raise NotImplementedError


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
    def add_data(
        self,
        data,
        name="New signal",
        _class=None,
        sampling=10,
        mask=[],
        plotter=None,
        colname=None,
    ):
        self.data.append(data)
        if name in self.names or name == "":
            name = "New_{}_{}".format(name, len(self.names))

        if len(name) > MAXNAMELEN:
            name = name[0:MAXNAMELEN]

        self.names.append(name)
        self.sampling.append(sampling)
        self.masks.append(mask)
        self.newdata.emit()

        if plotter is None:
            plotter, colname = choose_plotter(data)

        plotter.title = name

        if _class is None:
            _class = SignalViewer2(
                self.parent,
                data,
                title=self.names[-1],
                mask=self.masks[-1],
                plotter=plotter,
            )
            _class.plotter.colname = colname
            _class.display()

        self.add_viewer(_class, self.names[-1])

    def change_name(self, idx, name):
        self.names[idx] = name
        self.viewers[idx].plotter.title = name

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
        self.plotters.pop(index)

    def add_viewer(self, _class, name):
        if _class != None:
            gui = apptools.getApp().gui
            PluginManager.plugin_instances.append(_class)
            gui.container.add_data_layer(name)
            self.viewers.append(PluginManager.plugin_instances[-1])
        else:
            self.viewers.append([])

    def filter_data(self, index, IDs):
        assert "CellID" in self.data[index].dtype.names

        _filtered_idx = np.isin(self.data[index][:]["CellID"], IDs)
        _filtered = self.data[index][_filtered_idx]

        self.add_data(
            _filtered, name=self.names[index], sampling=self.sampling[index],
        )

    def duplicate_data(self, index=0):
        """Duplicates the current data

        Args:
            index (int, optional): index of the data to duplicate, according to self.data. Defaults to 0.
        """
        data = copy.deepcopy(self.data[index])
        name = "Duplicate of {}".format(self.names[index])

        self.add_data(
            data, name=name, sampling=self.sampling[index],
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
