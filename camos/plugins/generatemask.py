import numpy as np
# TODO: rethink how PyQt5 dependencies are loaded
from PyQt5.QtWidgets import *
from tasks.processing import Processing

class GenerateMask(Processing):
    def __init__(self, model=None, parent=None, input=None):
        super(GenerateMask, self).__init__(model, parent, input)
        self.output = None
        self.image = None
        self.finished.connect(self.output_to_imagemodel)
        self.analysis_name = "Extract Mask"
        # TODO: analysis metadata (description) for creating the menubars...

    def _run(self):
        # TODO: replace this by a simpler approach (i.e., used in FluoroSNNAP
        # WARNING: may not work in macOS if no GPU acceleration is available
        from cellpose import models

        # Nuclei model works the best in this case
        # TODO: gpu acceleration toggle, user selectable
        model = models.Cellpose(gpu=False, torch=False, model_type="nuclei")
        masks, _, _, _ = model.eval(self.image.image(0), diameter=None, channels=0)
        self.output = masks
        self.finished.emit()

    def initialize_UI(self):

        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]