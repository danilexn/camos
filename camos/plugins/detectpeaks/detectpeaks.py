# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator

import scipy.io
import scipy.signal
import numpy as np
from . import oopsi

from camos.tasks.analysis import Analysis


class DetectPeaks(Analysis):
    analysis_name = "Detect Peaks"

    def __init__(self, model=None, parent=None, signal=None):
        super(DetectPeaks, self).__init__(model, parent, input, name=self.analysis_name)
        self.model = model
        self.signal = signal
        self._methods = {
            "oopsi Fast": self._run_oopsi,
            "Template matching": self._run_template,
        }
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        output_type = [("CellID", "int"), ("Active", "float")]
        self.output = np.zeros(shape=(1, 1), dtype=output_type)

        thr = float(self.threshold.text())
        iter_max = int(self.max_iter.text())
        event_amplitude = float(self.amplitude.text())

        self.output = self.method(
            self.data,
            self.output,
            output_type,
            fps=self.sampling,
            thr=thr,
            iter_max=iter_max,
            event_amplitude=event_amplitude,
        )

    def display(self):
        if type(self.signal.list_datasets()) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "Peaks from {}".format(self.dataname), self, self.sampling
        )

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.signal.list_datasets())
        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

        self.methodlabel = QLabel("Detection method", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(self.methods)
        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)

        self.onlyDouble = QDoubleValidator()
        self.onlyInt = QIntValidator()

        self.max_iter_label = QLabel("Max Iterations (oopsi)", self.parent)
        self.max_iter = QLineEdit()
        self.max_iter.setValidator(self.onlyInt)
        self.max_iter.setText("50")
        self.layout.addWidget(self.max_iter_label)
        self.layout.addWidget(self.max_iter)

        self.threshold_label = QLabel("Threshold (template)", self.parent)
        self.threshold = QLineEdit()
        self.threshold.setValidator(self.onlyDouble)
        self.threshold.setText("0.85")
        self.layout.addWidget(self.threshold_label)
        self.layout.addWidget(self.threshold)

        self.amplitude_label = QLabel("Event Amplitude (template)", self.parent)
        self.amplitude = QLineEdit()
        self.amplitude.setValidator(self.onlyDouble)
        self.amplitude.setText("0.01")
        self.layout.addWidget(self.amplitude_label)
        self.layout.addWidget(self.amplitude)

    def _set_method(self, index):
        self.methodname = self.methods[index]
        self.method = self._methods[self.methodname]

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset
        self.dataname = self.signal.names[index]
        self.sampling = self.signal.sampling[index]

    def _update_values_plot(self, values):
        idx = np.isin(self.output[:]["CellID"], np.array(values))
        self.foutput = self.output[idx]

    def _plot(self):
        self.plot.axes.scatter(
            y=self.foutput[:]["CellID"], x=self.foutput[:]["Active"], s=0.5
        )
        self.plot.axes.set_ylabel("ROI ID")
        self.plot.axes.set_xlabel("Time (s)")

    @property
    def methods(self):
        return list(self._methods.keys())

    def _run_oopsi(self, data, output, output_type, **kwargs):
        fps = kwargs["fps"]
        iter_max = kwargs["iter_max"]

        data = self.data
        for i in range(data.shape[0]):
            F = data[i]
            db, Cz = oopsi.fast(F, dt=1 / fps, iter_max=iter_max)
            idxs = np.where(db >= 1)[0] / fps
            for idx in idxs:
                row = np.array([(i, idx)], dtype=output_type)
                output = np.append(output, row)
            self.intReady.emit(i * 100 / data.shape[0])

        return output

    def _run_template(self, data, output, output_type, **kwargs):
        fps = kwargs["fps"]
        thr = kwargs["thr"]
        event_amplitude = kwargs["event_amplitude"]
        spike_lib = scipy.io.loadmat("resources/spikes.mat")["spikes"][0]

        for cell in range(data.shape[0]):
            x = data[cell]
            xorig = x
            spks = []

            if fps > 10:
                x = scipy.signal.decimate(x, np.floor(fps / 10))
            elif fps < 10:
                x = np.interp(x, np.floor(10 / fps))

            # deltaF/F0 being used
            if max(x) < 10:
                height = event_amplitude
            # Either raw trace or intensity above background being used
            else:
                height = event_amplitude * min(x)

            events = np.zeros((len(spike_lib), len(x)))
            for i, _snippet in enumerate(spike_lib):
                snippet = _snippet[0]
                L = len(snippet)
                C = np.zeros(len(x))
                for j in range(len(x) - (L + 1)):
                    x_snippet = x[j : (j + L)]
                    if np.ptp(x_snippet) > height:
                        R = np.corrcoef(x_snippet, snippet)
                        C[j] = R[0, 1]
                events[i, :] = C

            spks = np.where(np.max(events, axis=0) >= thr)[0] / fps

            for spk in spks:
                row = np.array([(cell, spk)], dtype=output_type)
                output = np.append(output, row)

            self.intReady.emit(cell * 100 / data.shape[0])

        return output
