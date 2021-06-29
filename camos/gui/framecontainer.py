# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from camos.utils.cmaps import cmaps
import pyqtgraph as pg


class FrameContainer(QtWidgets.QWidget):
    """Contains the ViewPorts for the images and the signals in the model, as well as the sidebar containing the list of layers and the basic editing controls

    Args:
        QtWidgets (QWidget): base class
    """

    def __init__(self, parent):
        """Initialization of FrameContainer. Contains the layout for the viewports (divided in two boxes) and for the sidebar

        Args:
            parent (QtWidgets.QMainWindow): main window of the application
        """
        super(QtWidgets.QWidget, self).__init__()
        self.currentlayer = 0
        self.parent = parent
        self.setContentsMargins(0, 0, 0, 0)
        self.mainlayout = QtWidgets.QHBoxLayout(self)
        self.mainlayout.setSpacing(0)
        self.mainlayout.setContentsMargins(0, 0, 0, 0)
        self.verticalwidgets()

        self.mainlayout.addLayout(self.box_layout1, 1) # was 2 before
        # self.mainlayout.addLayout(self.box_layout2, 1)
        pg.QtGui.QApplication.processEvents()

    def verticalwidgets(self):
        """ViewPorts for the images (box_layout1)
        """
        # Left side
        self.box_layout1 = QtWidgets.QHBoxLayout()
        self.box_layout1_1 = QtWidgets.QVBoxLayout()
        self.box_layout1.setContentsMargins(0, 0, 0, 0)
        self.box_layout1.setSpacing(0)
        self.opened_layers_widget = QLayerWidget()
        self.opened_layers_widget.setSpacing(15)
        self._createLayersControls()
        self.opened_layers_widget.currentRowChanged.connect(
            self._change_LayersControls_values
        )

        self.opened_layers_widget.currentRowChanged.connect(
            self._change_current_layer
        )

        self.opened_layers_widget.itemDoubleClicked.connect(
            self._setup_current_layer
        )

        self.box_layout1_1.addWidget(self.opened_layers_widget, 1)
        self.box_layout1_1.addWidget(self.layers_controls, 1)
        self.box_layout1.addLayout(self.box_layout1_1, 1)
        self.box_layout1.addWidget(self.parent.viewport, 4)

        self._createLayersActions()
        self._createLayersToolBar()

        # Right side plot values selected!
        # self.box_layout2 = QtWidgets.QVBoxLayout()
        # self.box_layout2.setContentsMargins(0, 0, 0, 0)
        # self.box_layout2.addWidget(
        #    self.parent.signalviewport.scene.canvas.native
        # )

    def _change_current_layer(self, index):
        """Internal representation of the current layer selected

        Args:
            index (int): index of the currently selected layer
        """
        self.currentlayer = index

    def _update_layer_elements(self, layer):
        """When the ImageViewModel has updates in any of the elements, the layers list is updated

        Args:
            name (str): the name of the new layer to be added
        """
        name = self.parent.model.names[layer]
        item = QListWidgetItem(name)
        item.setIcon(QIcon(self.parent.model.get_icon(-1)))
        self.opened_layers_widget.addItem(item)
        maxframe = self.parent.model.maxframe
        self.current_frame_slider.setRange(0, maxframe - 1)

    def _setup_current_layer(self, layerName):
        text, okPressed = QInputDialog.getText(self, "Change '{}' name".format(layerName),"New name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            layer = self.opened_layers_widget.selectedIndexes()
            self.parent.model.names[layer[0].row()] = text
            items = self.opened_layers_widget.selectedItems()
            for item in items:
                item.setText(text)

    def _createLayersControls(self):
        """For the lateral layer control, creates the upper view of layers, and the bottom individual controls per layer
        """
        self.layers_controls = QGroupBox("Selected layer")
        layout = QFormLayout()
        self.opacity_layer_slider = QSlider(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Opacity:"), self.opacity_layer_slider)
        self.colormap_layer_selector = QComboBox()
        self._populate_colormaps()
        layout.addRow(QLabel("Colormap:"), self.colormap_layer_selector)
        self.contrast_layer_slider = QSlider(QtCore.Qt.Horizontal)
        self.contrast_layer_slider.setRange(-127, 127)
        self.contrast_layer_slider.setValue(0)
        layout.addRow(QLabel("Contrast:"), self.contrast_layer_slider)
        self.brightness_layer_slider = QSlider(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Brightness:"), self.brightness_layer_slider)
        self.brightness_layer_slider.setRange(-127, 127)
        self.brightness_layer_slider.setValue(0)
        self.scale_slider = QSlider(QtCore.Qt.Horizontal)
        self.apply_changes_layer_bt = QPushButton("Change")
        layout.addRow(QLabel("X-Y scale:"), self.scale_slider)
        self.scale_slider.setRange(-90, 100)
        self.scale_slider.setValue(10)
        self.apply_changes_layer_bt.clicked.connect(self._apply_changes_layer)
        layout.addRow(self.apply_changes_layer_bt)
        self.current_frame_slider = QScrollBar(QtCore.Qt.Horizontal)
        layout.addRow(QLabel("Current frame:"), self.current_frame_slider)
        self.current_frame_slider.valueChanged.connect(self._set_frame)
        self.layers_controls.setLayout(layout)

    def _populate_colormaps(self):
        """Inside the Layers Controls, populates the colormap controls with those available
        """
        self.colormap_layer_selector.addItems(cmaps)

    def _set_frame(self, t):
        """Configures the current frame, selected in the Layers Controls, to the image model

        Args:
            t (int): current frame selected in self.current_frame_slider
        """
        self.parent.model.set_frame(t)

    def _get_frame(self):
        """Returns the frame currently selected in the image model
        """
        self.parent.model.get_frame()

    def _get_max_frame(self):
        """Returns the maximum number of frames among all in the image model
        """
        self.parent.model.get_max_frame()

    def _change_LayersControls_values(self, index):
        """When a layer is selected in the sidebar, the controls will change to represent the layer's current properties

        Args:
            index (int): the index of the selected layer
        """
        op = self.parent.model.get_opacity(index)
        self.opacity_layer_slider.setValue(op)
        co = self.parent.model.get_contrast(index)
        self.contrast_layer_slider.setValue(co)
        br = self.parent.model.get_brightness(index)
        self.brightness_layer_slider.setValue(br)
        sc = self.parent.model.get_scale(index)
        self.scale_slider.setValue(sc)
        cm = self.parent.model.get_colormap(index)
        self.colormap_layer_selector.setCurrentIndex(
            list(cmaps.keys()).index(cm)
        )
        self.parent.model.currentlayer = index

    def _apply_changes_layer(self, **kwargs):
        """Retrieves the values from the layer controls, and puts them in the model. so it can refresh the representation of the image in the ViewPort
        """
        index = self.opened_layers_widget.currentRow()
        op = self.opacity_layer_slider.value()
        br = self.brightness_layer_slider.value()
        co = self.contrast_layer_slider.value()
        sc = self.scale_slider.value()
        sc = sc if sc != 0 else 10
        sc = 1/abs(sc) if sc < 0 else sc
        sc = sc/10
        cm = self.colormap_layer_selector.currentText()
        self.parent.model.set_values(op, br, co, cm, sc, index)

    def _createLayersActions(self):
        """Creates the UI elements (buttons) to handle Removal, Duplication, ROI toggling, Cropping and Cell Selection for the currently selected layer
        """
        # File actions
        self.removeAction = QAction(self)
        self.removeAction.setText("&Remove")
        self.removeAction.setIcon(QIcon("resources/icon-remove.svg"))
        self.removeAction.triggered.connect(self._layer_remove)
        self.duplicateAction = QAction(
            QIcon("resources/icon-duplicate.svg"), "&Duplicate", self
        )
        self.duplicateAction.triggered.connect(self._duplicate_layer)
        self.rotateAction = QAction(
            QIcon("resources/icon-rotate.svg"), "&Rotate", self
        )
        self.rotateAction.triggered.connect(self._rotate_layer)
        self.flipAction = QAction(
            QIcon("resources/icon-flip.svg"), "&Flip", self
        )
        self.flipAction.triggered.connect(self._flip_layer)
        self.toggleROIAction = QAction(
            QIcon("resources/icon-roi.svg"), "&ROI", self
        )
        self.toggleROIAction.triggered.connect(self._toggle_roi)
        self.cropAction = QAction(
            QIcon("resources/icon-crop.svg"), "&Crop", self
        )
        self.cropAction.triggered.connect(self._crop_layer)
        self.cellSelect = QAction(
            QIcon("resources/icon-neuron.svg"), "&Select Cell", self
        )
        self.cellSelect.triggered.connect(self._select_cells)
        self.resetAxis = QAction(
            QIcon("resources/reset-axis.svg"), "&Align zero", self
        )
        self.resetAxis.triggered.connect(self._reset_axis)
        self.sendMask = QAction(
            QIcon("resources/icon-all.svg"), "&Select All", self
        )
        self.sendMask.triggered.connect(self._send_mask)
        self.alignImage = QAction(
            QIcon("resources/icon-align.svg"), "&Align to", self
        )
        self.alignImage.triggered.connect(self._align_image)

    def _layer_remove(self):
        """Handles the removal of the currently selected layer in self.currentlayer, which is updated, in the image model
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.opened_layers_widget.takeItem(idx)
        self.parent.model.layer_remove(idx)

    def _duplicate_layer(self):
        """Handles the call to ImageViewModel.duplicate_image in the parent image model, so it can duplicate the currently selected layer in self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.duplicate_image(idx)

    def _crop_layer(self):
        """Handles the call to ImageViewModel.crop_image in the parent image model, so it can crop the currently selected layer in self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.crop_image(idx)

    def _reset_axis(self):
        """Handles the call to ImageViewModel.reset_position in the parent image model, so it can reset the current coordinates of self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.reset_position(idx)

    def _send_mask(self):
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.update_plots(idx)

    def _align_image(self):
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        dialog = LayerDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.parent.model.align_layers(dialog.combo.currentIndex())

    def _select_cells(self):
        """Handles the call to ImageViewModel.trigger_select_cells in the parent image model, so it can enable the selection of cells for any layer selected at any moment
        """
        self.parent.model.trigger_select_cells()

    def _toggle_roi(self):
        """Handles the call to ImageViewModel.toggle_roi
        """
        self.parent.viewport.toggle_roi()

    def _rotate_layer(self):
        """Handles the call to ImageViewModel.rotate_image in the parent image model, so it can perform anticlockwise rotation for the selected self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.rotate_image(idx)

    def _flip_layer(self):
        """Handles the call to ImageViewModel.rotate_image in the parent image model, so it can perform anticlockwise rotation for the selected self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.flip_image(idx)

    def _createLayersToolBar(self):
        """Creates the toolbar inside the layers sidebar containing the buttons for Remove, Duplicate, Rotate, Toggle ROI, Crop and Select Cell actions.
        """
        # File toolbar
        layersToolBar = self.parent.addToolBar("layers")
        layersToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        layersToolBar.addAction(self.removeAction)
        layersToolBar.addAction(self.duplicateAction)
        layersToolBar.addAction(self.rotateAction)
        layersToolBar.addAction(self.flipAction)
        layersToolBar.addAction(self.toggleROIAction)
        layersToolBar.addAction(self.cropAction)
        layersToolBar.addAction(self.resetAxis)
        layersToolBar.addAction(self.alignImage)
        layersToolBar.addAction(self.cellSelect)
        layersToolBar.addAction(self.sendMask)


class QLayerWidget(QtWidgets.QListWidget):

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            row = self.currentRow()
            self.parent()._layer_remove()
        else:
            super().keyPressEvent(event)

class LayerDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LayerDialog, self).__init__(parent)

        label = QtGui.QLabel("Text")
        self.combo = QtGui.QComboBox()
        self.parent = parent
        self.combo.addItems(self.parent.model.list_images())

        box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QtGui.QGridLayout(self)
        lay.addWidget(label, 0, 0)
        lay.addWidget(self.combo, 0, 1)
        lay.addWidget(box, 2, 0, 1, 2)

        self.resize(640, 240)