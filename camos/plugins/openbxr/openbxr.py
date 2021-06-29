# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, pyqtSignal

import numpy as np
import h5py

from camos.tasks.opening import Opening
from camos.viewport.signalviewer import SignalViewer


class OpenBXR(Opening):
    """This is the plugin to load CMOS data into CaMOS, being able to select the electrodes
    """

    finished = pyqtSignal()
    plotReady = pyqtSignal()
    gridReady = pyqtSignal(np.ndarray)
    intReady = pyqtSignal(int)
    analysis_name = "Open bxr file"

    def __init__(self, parent=None, **kwargs):
        """Initialization of the object

        Args:
            model ([type], optional): [description]. Defaults to None.
            signal ([type], optional): [description]. Defaults to None.
            parent ([type], optional): [description]. Defaults to None.
            signal ([type], optional): [description]. Defaults to None.
            file ([type], optional): [description]. Defaults to None.
        """
        super(OpenBXR, self).__init__(
            None,
            parent,
            None,
            name=self.analysis_name,
            extensions="BXR File (*.bxr)",
            show=False,
        )
        self.parent = parent

    def _run(self):
        filehdf5_bxr = h5py.File(self.filename)
        samplingRate = np.asarray(filehdf5_bxr["3BRecInfo"]["3BRecVars"]["SamplingRate"])[0]
        SpikeChIDs = np.asarray(filehdf5_bxr["3BResults"]["3BChEvents"]["SpikeChIDs"])
        SpikeTimes = np.asarray(filehdf5_bxr["3BResults"]["3BChEvents"]["SpikeTimes"])/samplingRate

        output_type = [('CellID', 'int'), ('Active', 'float')]
        self.output = np.zeros(shape = (len(SpikeChIDs), 1), dtype = output_type)
        self.output[:]["CellID"] = SpikeChIDs.reshape(-1, 1)
        self.output[:]["Active"] = SpikeTimes.reshape(-1, 1)

        _sv = SignalViewer(self.parent, self.output)

        self.parent.signalmodel.add_data(self.output, "Events from BXR".format(), _sv, samplingRate)
        _sv.display()

    def h5printR(self, item, leading=''):
        for key in item:
            if isinstance(item[key], h5py.Dataset):
                print(leading + key + ' : ' + str(item[key].shape))
            else:
                print(leading + key)
                self.h5printR(item[key], leading + ' ')

    def h5print(self, filename):
        with h5py.File(filename, 'r') as h:
            print(filename)
            self.h5printR(h, '  ')
