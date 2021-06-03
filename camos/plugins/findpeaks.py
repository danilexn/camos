import numpy as np
# TODO: rethink how PyQt5 dependencies are loaded
from PyQt5.QtWidgets import *
from tasks.analysis import Analysis

class FindPeaks(Analysis):
    def __init__(self, model=None, parent=None, input=None):
        super(FindPeaks, self).__init__(model, parent, input)
        self.mask = None
        self.image = None
        self.analysis_name = "Find Peaks from Signal"
        self.finished.connect(self.output_to_signalmodel)

    # WARNING: this code is naive and slow.
    # TODO: make it faster, replace np.where by, e.g., a coordinate map of the mask.
    def _run(self):
        self.output = np.zeros((self.mask.max, self.image.frames))
        total = int(self.mask.max)
        for i in range(1, self.mask.max):
            cell = self.mask.image(0) == i
            cell = cell[np.newaxis, :, :]
            self.output[i, :] = np.sum(np.where(cell > 0, self.image._image._imgs, 0), axis = (1, 2))
            self.intReady.emit(i * 100 / total)

        self.finished.emit()

    def initialize_UI(self):
        self.masklabel = QLabel("Algorithm", self.dockUI)
        self.imagelabel = QLabel("Signal data", self.dockUI)
        self.cbmask = QComboBox()
        self.cbmask.currentIndexChanged.connect(self._set_mask)
        self.cbmask.addItems(self.model.list_images())
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    # TODO: rewrite these methods as properties
    def _set_mask(self, index):
        self.mask = self.model.images[index]

    def _set_image(self, index):
        self.image = self.model.images[index]