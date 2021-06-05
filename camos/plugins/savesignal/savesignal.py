#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import h5py


class SaveSignal(Saving):
    def __init__(self, model=None, signal=None, parent=None, input=None, file=None):
        super(SaveSignal, self).__init__(
            model, parent, input, name="Save Signal", extensions="hdf5 File (*.h5)"
        )
        self.file = file
        self.image = None
        self.signalmodel = signal
        self.analysis_name = "Save Signals"

    def _run(self):
        h5f = h5py.File(self.file, "w")
        for i, data in enumerate(self.signal):
            h5f.create_dataset("signal_{}".format(i), data=data)
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
