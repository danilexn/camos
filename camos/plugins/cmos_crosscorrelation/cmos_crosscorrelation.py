# -*- coding: utf-8 -*-
# Created on Wed Jul 07 2021
# Last modified on Wed Jul 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from camos.tasks.analysis import Analysis

from camos.utils.generategui import (
    DatasetInput,
    NumericInput,
)

class CmosCrossCorrelation(Analysis):
    analysis_name = "Cross correlation of Electrodes"
    required = ["dataset"]
    
    
    def __init__(self, model=None, parent=None, signal=None):
        super(CmosCrossCorrelation, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self,
        duration: NumericInput("Recording duration in seconds", 600),
        electrode_x: NumericInput("Number of electrodes along one axis",64),
        plot_type: NumericInput("Plot type: 0 for crosscorr matrix; 1 for network graph",0),
        _i_data: DatasetInput("Source Dataset", 0)
        ):

        output_type = [("CellID1", "int"),("CellID2","int"), ("correlation", "float")]
        self.duration = duration
        self.electrode_n = electrode_x

        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        print(data)
        self.output = np.zeros(shape=(len(100), 1), dtype=output_type)

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "CrossCorrelation of {}".format(self.dataname), self)

    def _plot(self):
        mfr = np.zeros(shape=(self.electrode_n * self.electrode_n))

        # reshape mfr values in shape of chip for heatmap 
        mfr = np.reshape(mfr,(self.electrode_n,self.electrode_n))

        im = self.plot.axes.imshow(
            mfr, cmap="inferno", origin="upper"
        )

        self.plot.fig.colorbar(
            im, ax=self.plot.axes, label="Mean Firing Rate (Events/s)")

        self.plot.axes.set_ylabel("Electrode in Y direction")
        self.plot.axes.set_xlabel("Electrode in X direction")
