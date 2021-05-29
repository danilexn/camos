from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from utils.cmaps import cmaps
import pyqtgraph as pg

class FrameContainer(QtWidgets.QWidget):
    def __init__(self, parent):
        super(QtWidgets.QWidget, self).__init__()
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)
        self.mainlayout = QtWidgets.QHBoxLayout(self)
        self.mainlayout.setSpacing(0)
        self.mainlayout.setContentsMargins(0, 0, 0, 0)
        self.verticalwidgets()

        self.mainlayout.addLayout(self.box_layout1, 2)
        self.mainlayout.addLayout(self.box_layout2, 1)
        pg.QtGui.QApplication.processEvents()

    def verticalwidgets(self):
        # Left side
        self.box_layout1 = QtWidgets.QHBoxLayout()
        self.box_layout1_1 = QtWidgets.QVBoxLayout()
        self.box_layout1.setContentsMargins(0, 0, 0, 0)
        self.box_layout1.setSpacing(0)
        self.opened_layers_widget = QListWidget()
        self.opened_layers_widget.setSpacing(15)
        self._createLayersControls()
        self.opened_layers_widget.currentRowChanged.connect(
            self._change_LayersControls_values
        )

        self.box_layout1_1.addWidget(self.opened_layers_widget, 1)
        self.box_layout1_1.addWidget(self.layers_controls, 1)
        self.box_layout1.addLayout(self.box_layout1_1, 1)
        self.box_layout1.addWidget(self.parent.viewport, 4)

        self._createLayersActions()
        self._createLayersToolBar()

        # Right side plot values selected!
        self.box_layout2 = QtWidgets.QVBoxLayout()
        self.box_layout2.setContentsMargins(0, 0, 0, 0)
        self.box_layout2.addWidget(self.parent.signalviewport.scene.canvas.native)

    def _update_layer_elements(self, name):
        item = QListWidgetItem(name)
        item.setIcon(QIcon(self.parent.model.get_icon(-1)))
        self.opened_layers_widget.addItem(item)
        maxframe = self.parent.model.maxframe
        self.current_frame_slider.setRange(0, maxframe - 1)

    def _createLayersControls(self):
        self.layers_controls = QGroupBox("Selected layer")
        layout = QFormLayout()
        self.opacity_layer_slider = QSlider(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Opacity:"), self.opacity_layer_slider)
        self.colormap_layer_selector = QComboBox()
        self._populate_colormaps()
        layout.addRow(QLabel("Colormap:"), self.colormap_layer_selector)
        self.contrast_layer_slider = QSlider(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Contrast:"), self.contrast_layer_slider)
        self.brightness_layer_slider = QSlider(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Brightness:"), self.brightness_layer_slider)
        self.apply_changes_layer_bt = QPushButton("Change")
        self.apply_changes_layer_bt.clicked.connect(self._apply_changes_layer)
        layout.addRow(self.apply_changes_layer_bt)
        self.current_frame_slider = QScrollBar(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Current frame:"), self.current_frame_slider)
        self.current_frame_slider.valueChanged.connect(self._set_frame)
        self.layers_controls.setLayout(layout)

    def _populate_colormaps(self):
        self.colormap_layer_selector.addItems(cmaps.keys())

    def _set_frame(self, t):
        self.parent.model.set_frame(t)

    def _get_frame(self, t):
        self.parent.model.get_frame()

    def _get_max_frame(self, t):
        self.parent.model.get_max_frame()

    def _change_LayersControls_values(self, index):
        op = self.parent.model.get_opacity(index)
        self.opacity_layer_slider.setValue(op)
        cm = self.parent.model.get_colormap(index)
        self.colormap_layer_selector.setCurrentIndex(list(cmaps.keys()).index(cm))

    def _apply_changes_layer(self):
        index = self.opened_layers_widget.currentRow()
        op = self.opacity_layer_slider.value()
        self.parent.model.set_opacity(op, index)
        cm = self.colormap_layer_selector.currentText()
        self.parent.model.set_colormap(cm, index)

    def _createLayersActions(self):
        # File actions
        self.removeAction = QAction(self)
        self.removeAction.setText("&Remove")
        self.removeAction.setIcon(QIcon("resources/icon-remove.svg"))
        self.removeAction.triggered.connect(
            lambda idx=self.opened_layers_widget.currentRow(): self._layer_remove(idx)
        )
        self.openAction = QAction(QIcon("resources/icon-duplicate.svg"), "&Duplicate", self)
        self.saveAction = QAction(QIcon("resources/icon-rotate.svg"), "&Rotate", self)

    def _layer_remove(self, idx):
        self.opened_layers_widget.takeItem(idx)
        self.parent.model.layer_remove(idx)

    def _createLayersToolBar(self):
        # File toolbar
        layersToolBar = self.parent.addToolBar("layers")
        layersToolBar.addAction(self.removeAction)
        layersToolBar.addAction(self.openAction)
        layersToolBar.addAction(self.saveAction)