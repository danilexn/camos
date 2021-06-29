# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import h5py


class SaveSignal(Saving):
    analysis_name = "Save Signals"

    def __init__(self, model=None, signal=None, parent=None, file=None):
        super(SaveSignal, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            extensions="hdf5 File (*.h5)",
        )
        self.signal = signal

    def _run(self):
        h5f = h5py.File(self.filename, "w")
        for i, (name, data) in enumerate(self.signal):
            if len(self.signal.masks[i]) > 0:
                group_name = "{}".format(name)
                h5f.create_group(group_name)
                h5f[group_name].create_dataset(group_name, data = data)
                h5f[group_name].create_dataset("mask", data = self.signal.masks[i])
            else:
                h5f.create_dataset("{}".format(name), data=data)
        h5f.close()

    def initialize_UI(self):
        self.signallabel = QLabel("Signal tracks", self.dockUI)
        self.cbsignal = QComboBox()
        self.cbsignal.currentIndexChanged.connect(self._set_signal)
        self.cbsignal.addItems(self.signalmodel.list_signals())

        self.layout.addWidget(self.signallabel)
        self.layout.addWidget(self.cbsignal)

    def _set_signal(self, index):
        self.signal = self.signalmodel.data[index]
