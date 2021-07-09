# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import (
    DatasetInput,
    NumericInput,
)


class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"
    required = ["dataset"]

    def __init__(self, model=None, parent=None, signal=None):
        super(MeanFiringRate, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(
        self,
        duration: NumericInput("Recording duration in seconds", 600),
        electrode_x: NumericInput("Number of electrodes along one axis",64),
        #scale: NumericInput("Axis scale", 1),
        #_i_units: CustomComboInput(list(length.keys()), "Axis units", 0),
        _i_data: DatasetInput("Source Dataset", 0),

    ):
        output_type = [("CellID", "int"), ("MFR", "float")]
        self.duration = duration
        self.electrode_n = electrode_x

        '''
        Data format:

        First column is electrode ID
        Second column is time of event
            ('CellID', 'Active')
            [[(1520, 2.64562191e-03)]
            [(4038, 5.58520180e-03)]
            [(3245, 6.39358627e-03)]
        
        If electrode 1520 has 500 spike events, then there are 500 rows with ID 1520
        '''

        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]

        # Calculate mean firing rate per cell
        ROIs = np.unique(data[:]["CellID"])
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)

        #get the event counts and make CellID unique
        unique, counts = np.unique(data[:]["CellID"], return_counts=True)
        self.output[:]["CellID"] = unique.reshape(-1, 1)
        self.output[:]["MFR"] = counts.reshape(-1, 1)
        self.output[:]["MFR"] = self.output[:]["MFR"]/self.duration

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "MFR of {}".format(self.dataname), self)

    def _plot(self):
        mfr = np.zeros(shape=(self.electrode_n * self.electrode_n))

        for idx,i in enumerate(self.output[:]["CellID"]):
            mfr[i] = self.output[idx]["MFR"]

        # reshape mfr values in shape of chip for heatmap 
        mfr = np.reshape(mfr,(self.electrode_n,self.electrode_n))

        im = self.plot.axes.imshow(
            mfr, cmap="inferno", origin="upper"
        )

        self.plot.fig.colorbar(
            im, ax=self.plot.axes, label="Mean Firing Rate (Events/s)")

        self.plot.axes.set_ylabel("Electrode in Y direction")
        self.plot.axes.set_xlabel("Electrode in X direction")
