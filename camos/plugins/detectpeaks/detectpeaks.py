# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import scipy.io
import scipy.signal
import numpy as np
from . import oopsi

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, DatasetInput, CustomComboInput
from camos.utils.units import get_time


class DetectPeaks(Analysis):
    analysis_name = "Detect Peaks"
    required = ["dataset"]

    def __init__(self, model=None, parent=None, signal=None):
        super(DetectPeaks, self).__init__(model, parent, input, name=self.analysis_name)
        self.model = model
        self.signal = signal
        self._methods = {
            "oopsi Fast": self._run_oopsi,
            "Template matching": self._run_template,
        }

    def _run(
        self,
        thr: NumericInput("Threshold (template)", 0.85),
        iter_max: NumericInput("Max Iterations (oopsi)", 50),
        event_amplitude: NumericInput("Event Amplitude (Template)", 0.01),
        _i_data: DatasetInput("Source dataset", 0),
        _i_method: CustomComboInput(
            ["oopsi Fast", "Template matching"], "Detection method", 0
        ),
    ):
        data = self.signal.data[_i_data]
        sampling = self.signal.sampling[_i_data]
        output_type = [("CellID", "int"), ("Active", "float")]
        method = self._methods[list(self._methods.keys())[_i_method]]
        self.dataname = self.signal.names[_i_data]
        self.output = np.zeros(shape=(1, 1), dtype=output_type)

        self.output = method(
            data,
            self.output,
            output_type,
            fps=sampling,
            thr=thr,
            iter_max=iter_max,
            event_amplitude=event_amplitude,
        )

    @property
    def methods(self):
        return list(self._methods.keys())

    def _run_oopsi(self, data, output, output_type, **kwargs):
        fps = kwargs["fps"]
        iter_max = kwargs["iter_max"]

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
