import numpy as np
# TODO: rethink how PyQt5 dependencies are loaded
from PyQt5.QtWidgets import *
from tasks.processing import Processing

import cv2
import h5py

class SaveSignal(Processing):
    def __init__(self, model=None, signal = None, parent=None, input=None, file = None):
        super(SaveSignal, self).__init__(model, parent, input)
        self.file = file
        self.image = None
        self.signalmodel = signal
        self.analysis_name = "Save Signals"

    def _run(self):
        h5f = h5py.File(self.file, 'w')
        for i, data in enumerate(self.signal):
            h5f.create_dataset('signal_{}'.format(i), data=data)
        h5f.close()
        self.finished.emit()

    def initialize_UI(self):
        self.signallabel = QLabel("Signal tracks", self.dockUI)
        self.cbsignal = QComboBox()
        self.cbsignal.currentIndexChanged.connect(self._set_signal)
        self.cbsignal.addItems(self.signalmodel.list_signals())

        self.layout.addWidget(self.signallabel)
        self.layout.addWidget(self.cbsignal)

    def _set_signal(self, index):
        self.signal = self.signalmodel.data[index]