from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QComboBox
from PyQt5.QtGui import QDoubleValidator

import camos.utils.apptools as apptools

colors = {"Black": (0, 0, 0), "White": (255, 255, 255)}


class CAMOSPreferences(QtGui.QDialog):
    def __init__(self, parent=None):
        self.parent = parent

        if parent == None:
            self.parent = apptools.getGui()

        self.gui = apptools.getGui()

        super(CAMOSPreferences, self).__init__(parent)

        self.model = self.parent.model

        self.setWindowTitle("CaMOS Preferences")

        self.bgcollabel = QLabel("Background Color")
        self.cbbgcol = QComboBox()
        self.cbbgcol.addItems(colors.keys())

        box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QtGui.QGridLayout(self)
        lay.addWidget(self.bgcollabel)
        lay.addWidget(self.cbbgcol)
        lay.addWidget(box)
        self.show()

    def accept(self):
        self.apply_changes_viewport()
        super().accept()

    def apply_changes_viewport(self):
        color = colors[list(colors.keys())[self.cbbgcol.currentIndex()]]
        self.gui.viewport.change_background(color)
