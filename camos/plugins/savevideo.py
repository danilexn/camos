import numpy as np
# TODO: rethink how PyQt5 dependencies are loaded
from PyQt5.QtWidgets import *
from tasks.processing import Processing

import cv2

class SaveVideo(Processing):
    def __init__(self, model=None, signal = None, parent=None, input=None, file = None):
        super(SaveVideo, self).__init__(model, parent, input)
        self.file = file
        self.image = None
        self.analysis_name = "Save Video"

    def _run(self):
        height, width, layers = self.model.get_current_view(0).shape
        size = (width,height)
        out = cv2.VideoWriter(self.file,cv2.VideoWriter_fourcc(*'DIVX'), int(self.fps.text()), size)
        for i in range(self.model.maxframe):
            self.model.frame = i
            out.write(np.uint8(self.model.get_current_view()))
            self.intReady.emit(i * 100 / self.model.maxframe)

        out.release()
        self.finished.emit()

    def initialize_UI(self):
        self.fpslabel = QLabel("Frames per second", self.dockUI)
        self.fps = QLineEdit()

        self.layout.addWidget(self.fpslabel)
        self.layout.addWidget(self.fps)