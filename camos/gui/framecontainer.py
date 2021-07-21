# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Thu Jul 15 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QListWidgetItem,
    QInputDialog,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QSlider,
    QLabel,
    QComboBox,
    QAction,
    QWidget,
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt

import pyqtgraph as pg

from camos.utils.cmaps import cmaps
from camos.utils.units import get_length
from camos.utils.strings import range_to_list
from camos.viewport.tableviewer import TableViewer
from camos.resources import resources

MAXNAMELEN = 30


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

        self.mainlayout.addLayout(self.box_layout1, 1)
        pg.QtGui.QApplication.processEvents()

    def verticalwidgets(self):
        """ViewPorts for the images (box_layout1)
        """
        # Create toolbar
        self._createLayersActions()
        self._createLayersToolBar()

        # Left side
        self.box_layout1 = QtWidgets.QHBoxLayout()
        self.box_layout1_1 = QtWidgets.QVBoxLayout()
        self.box_layout1.setContentsMargins(0, 0, 0, 0)
        self.box_layout1.setSpacing(0)
        self.opened_data = TabWidget()
        self.opened_data.currentChanged.connect(self._tab_change)
        self.opened_layers_widget = QLayerWidget(self)
        self.opened_data.addTab(self.opened_layers_widget, "Layers")
        self.opened_layers_widget.installEventFilter(self)
        self._createLayersControls()
        self.opened_layers_widget.currentRowChanged.connect(
            self._change_LayersControls_values
        )
        self.opened_layers_widget.setSpacing(5)
        self.opened_layers_widget.currentRowChanged.connect(self._change_current_layer)
        self.opened_layers_widget.itemDoubleClicked.connect(self._layer_toggle)
        self.opened_data_widget = QDataWidget(self)
        self.opened_data_widget.itemDoubleClicked.connect(self.open_data_layer)
        self.opened_data_widget.installEventFilter(self)
        self.opened_data.addTab(self.opened_data_widget, "Datasets")

        self.box_layout1_1.addWidget(self.opened_data, 5)
        self.box_layout1_1.addWidget(self.layers_controls, 1)
        self.box_layout1.addLayout(self.box_layout1_1, 1)
        self.box_layout1.addWidget(self.parent.viewport, 4)

    def _change_current_layer(self, index):
        """Internal representation of the current layer selected

        Args:
            index (int): index of the currently selected layer
        """
        self.currentlayer = index
        self.parent.model.currentlayer = index

    def _update_layer_elements(self, layer):
        """When the ImageViewModel has updates in any of the elements, the layers list is updated

        Args:
            name (str): the name of the new layer to be added
        """
        name = self.parent.model.names[layer]
        _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
        item = QListWidgetItem(_s_name)
        item.setIcon(QIcon(self.parent.model.get_icon(layer)))
        item.setToolTip(name + " (double click to toggle visibility)")
        self.opened_layers_widget.addItem(item)
        self.opened_layers_widget.setCurrentItem(item)

    def add_data_layer(self, name):
        """When the ImageViewModel has updates in any of the elements, the layers list is updated

        Args:
            name (str): the name of the new layer to be added
        """
        _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
        item = QListWidgetItem(_s_name)
        item.setToolTip(name + " (double click to display)")
        self.opened_data_widget.addItem(item)

    def open_data_layer(self):
        idx = self.opened_data_widget.currentRow()
        self.parent.signalmodel.viewers[idx].show()

    def _setup_current_layer(self):
        text, okPressed = QInputDialog.getText(
            self, "Change name", "New name:", QLineEdit.Normal, "",
        )
        if okPressed and text != "":
            layer = self.opened_layers_widget.selectedIndexes()
            self.parent.model.names[layer[0].row()] = text
            items = self.opened_layers_widget.selectedItems()
            for item in items:
                _s_name = text if len(text) < MAXNAMELEN else text[0:MAXNAMELEN] + "..."
                item.setText(_s_name)
                item.setToolTip(text + " (double click to display)")

    def _setup_current_data(self):
        text, okPressed = QInputDialog.getText(
            self, "Change name", "New name:", QLineEdit.Normal, "",
        )
        if okPressed and text != "":
            layer = self.opened_data_widget.selectedIndexes()
            self.parent.signalmodel.change_name(layer[0].row(), text)
            items = self.opened_data_widget.selectedItems()
            for item in items:
                _s_name = text if len(text) < MAXNAMELEN else text[0:MAXNAMELEN] + "..."
                item.setText(_s_name)
                item.setToolTip(text + " (double click to display)")

    def _createLayersControls(self):
        """For the lateral layer control, creates the upper view of layers, and the bottom individual controls per layer
        """
        # General appearance of the controls layout
        self.layers_controls = QGroupBox("  Selected layer")
        self.layers_controls.setContentsMargins(50, 100, 50, 80)
        layout = QFormLayout()
        layout.horizontalSpacing = 10

        # We create the following controls that act over the chosen layer
        # 1. Opacity
        self.opacity_layer_slider = QSlider(QtCore.Qt.Horizontal)
        self.opacity_layer_label = QLabel("")
        self.opacity_layer_slider.setRange(0, 100)
        layout.addRow(QLabel("Opacity"))
        layout.addRow(self.opacity_layer_label, self.opacity_layer_slider)
        self.opacity_layer_slider.valueChanged.connect(self._apply_changes_layer)
        self.opacity_layer_slider.valueChanged.connect(self.opacityLabelUpdate)
        self.opacity_layer_slider.setValue(50)

        # 2. Colormap
        self.colormap_layer_selector = QComboBox()
        self._populate_colormaps()
        layout.addRow(QLabel("Colormap"))
        layout.addRow(self.colormap_layer_selector)
        self.colormap_layer_selector.activated.connect(self._apply_changes_layer)

        # Configure the layout
        self.layers_controls.setLayout(layout)

    def opacityLabelUpdate(self, value):
        self.opacity_layer_label.setText(str(value))

    def _populate_colormaps(self):
        """Inside the Layers Controls, populates the colormap controls with those available
        """
        self.colormap_layer_selector.addItems(cmaps)

    # def _set_frame(self, t):
    #     """Configures the current frame, selected in the Layers Controls, to the image model

    #     Args:
    #         t (int): current frame selected in self.current_frame_slider
    #     """
    #     self.parent.model.set_frame(t)

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
        cm = self.parent.model.get_colormap(index)
        self.colormap_layer_selector.setCurrentIndex(list(cmaps.keys()).index(cm))

    def _apply_changes_layer(self, **kwargs):
        """Retrieves the values from the layer controls, and puts them in the model. so it can refresh the representation of the image in the ViewPort
        """
        index = self.opened_layers_widget.currentRow()
        op = self.opacity_layer_slider.value()
        cm = self.colormap_layer_selector.currentText()
        _op = self.parent.model.get_opacity(index)
        _cm = self.parent.model.get_colormap(index)

        if op == _op and cm == _cm:
            return
        self.parent.model.set_values(op, cm, index)

    def _createLayersActions(self):
        """Creates the UI elements (buttons) to handle Removal, Duplication, ROI toggling, Cropping and Cell Selection for the currently selected layer
        """
        # File actions
        self.removeAction = QAction(self)
        self.removeAction.setText("&Remove")
        self.removeAction.setIcon(QIcon(":/resources/icon-remove.svg"))
        self.removeAction.setToolTip(
            "Removes the currently selected image (or dataset) layer"
        )
        self.removeAction.triggered.connect(self._button_remove)
        self.duplicateAction = QAction(
            QIcon(":/resources/icon-duplicate.svg"), "&Duplicate", self
        )
        self.duplicateAction.triggered.connect(self._button_duplicate)
        self.duplicateAction.setToolTip(
            "Duplicates the currently selected image (or dataset) layer"
        )
        self.rotateAction = QAction(
            QIcon(":/resources/icon-rotate.svg"), "&Rotate", self
        )
        self.rotateAction.triggered.connect(self._rotate_layer)
        self.rotateAction.setToolTip(
            "Creates a new image that is a 90 degree rotation of the currently selected image"
        )
        self.flipAction = QAction(QIcon(":/resources/icon-flip.svg"), "&Flip", self)
        self.flipAction.triggered.connect(self._flip_layer)
        self.flipAction.setToolTip(
            "Creates a new image that is a horizontal flip of the currently selected image"
        )
        self.toggleROIAction = QAction(QIcon(":/resources/icon-roi.svg"), "&ROI", self)
        self.toggleROIAction.triggered.connect(self._toggle_roi)
        self.toggleROIAction.setToolTip("Toggles the ROI selector On or Off")
        self.cropAction = QAction(QIcon(":/resources/icon-crop.svg"), "&Crop", self)
        self.cropAction.triggered.connect(self._crop_layer)
        self.cropAction.setToolTip(
            """Creates a new image that is a cropped version of the
currently selected layer, within the ROI coordinates"""
        )
        self.cellSelect = QAction(
            QIcon(":/resources/icon-neuron.svg"), "&Select Cell", self
        )
        self.cellSelect.triggered.connect(self._select_cells)
        self.cellSelect.setToolTip(
            """Toggles the selection of cells On or Off. When double clicking,
a new image filtered by the value of the double-clicked pixel will be
created from the currently selected layer"""
        )
        self.findIDs = QAction(QIcon(":/resources/icon-find.svg"), "&Find IDs", self)
        self.findIDs.triggered.connect(self._find_ids)
        self.findIDs.setToolTip(
            """For the currently selected image (or data) layer, you will be prompted
to introduce a list of IDs to filter. A new image (or data) layer will be
created filtered by the introduced IDs."""
        )
        self.resetAxis = QAction(
            QIcon(":/resources/reset-axis.svg"), "&Align zero", self
        )
        self.resetAxis.triggered.connect(self._reset_axis)
        self.resetAxis.setToolTip(
            """For the currently selected image, the position will be restored to the
global (0, 0) coordinate of the viewport."""
        )
        self.sendMask = QAction(QIcon(":/resources/icon-all.svg"), "&Select All", self)
        self.sendMask.triggered.connect(self._send_mask)
        self.sendMask.setToolTip(
            """For the currently selected layer, all unique values will be used to filter
the IDs displayed in all plots (e.g., Y-axis in a raster plot)"""
        )
        self.alignImage = QAction(
            QIcon(":/resources/icon-align.svg"), "&Align to", self
        )
        self.alignImage.triggered.connect(self._align_image)
        self.alignImage.setToolTip(
            """For the currently selected layer, you will be prompted to select another
layer which will be aligned/moved to its same position (top-left corner)"""
        )
        self.sumLayers = QAction(QIcon(":/resources/icon-sum.svg"), "&Sum", self)
        self.sumLayers.triggered.connect(self._sum_layers)
        self.sumLayers.setToolTip(
            """A new image will be generated as the sum of two images: the currently
selected layer and another layer you are prompted to select."""
        )
        self.subtractLayers = QAction(
            QIcon(":/resources/icon-subtract.svg"), "&Subtract", self
        )
        self.subtractLayers.triggered.connect(self._subtract_layers)
        self.subtractLayers.setToolTip(
            """A new image will be generated as the difference of two images:
the currently selected layer and another layer you are prompted to select."""
        )
        self.intersectLayers = QAction(
            QIcon(":/resources/icon-multiply.svg"), "&Intersect", self
        )
        self.intersectLayers.triggered.connect(self._intersect_layers)
        self.intersectLayers.setToolTip(
            """A new image will be generated as the intersection (pixel value different to 0)
of two images: the currently selected layer and another layer you select."""
        )

    def _button_remove(self):
        if self.opened_data.currentIndex() == 0:
            self._layer_remove()
        else:
            self._data_remove()

    def _button_duplicate(self):
        if self.opened_data.currentIndex() == 0:
            self._duplicate_layer()
        else:
            self._duplicate_data()

    def _layer_remove(self):
        """Handles the removal of the currently selected layer in self.currentlayer, which is updated, in the image model
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.opened_layers_widget.takeItem(idx)
        self.parent.model.layer_remove(idx)

    def _data_remove(self):
        """Handles the removal of the currently selected layer in self.currentlayer, which is updated, in the image model
        """
        self.currentlayer = self.opened_data_widget.currentRow()
        idx = self.currentlayer
        self.opened_data_widget.takeItem(idx)
        self.parent.signalmodel.data_remove(idx)

    def _layer_toggle(self):
        """Handles the removal of the currently selected layer in self.currentlayer, which is updated, in the image model
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.viewport.toggle_visibility(idx)
        current_c = (
            self.opened_layers_widget.currentItem().background().color().getRgb()
        )
        if current_c[0] == 102:
            self.opened_layers_widget.currentItem().setBackground(
                QtGui.QColor("#191919")
            )
        else:
            self.opened_layers_widget.currentItem().setBackground(
                QtGui.QColor("#666666")
            )

    def _layer_prefs(self):
        """Handles the removal of the currently selected layer in self.currentlayer, which is updated, in the image model
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        dialog = LayerPrefsDialog(self.parent, self.parent.model, idx)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.parent.model.update_prefs(
                idx,
                float(dialog.samplRate.text()),
                float(dialog.pxSize.text()),
                float(dialog.scaleSize.text()),
            )

    def _duplicate_layer(self):
        """Handles the call to ImageViewModel.duplicate_image in the parent image model, so it can duplicate the currently selected layer in self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.model.duplicate_image(idx)

    def _duplicate_data(self):
        """Handles the call to ImageViewModel.duplicate_image in the parent image model, so it can duplicate the currently selected layer in self.currentlayer
        """
        self.currentlayer = self.opened_layers_widget.currentRow()
        idx = self.currentlayer
        self.parent.signalmodel.duplicate_data(idx)

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
        id_list = self.parent.model.update_plots(idx)
        self.parent.signalmodel.filter_data(
            self.opened_data_widget.currentRow(), id_list
        )

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

    def _sum_layers(self):
        dialog = LayerDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.parent.model.sum_layers(dialog.combo.currentIndex())

    def _subtract_layers(self):
        dialog = LayerDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.parent.model.subtract_layers(dialog.combo.currentIndex())

    def _intersect_layers(self):
        dialog = LayerDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.parent.model.intersect_layers(dialog.combo.currentIndex())

    def _find_ids(self):
        dialog = TextDialog(self.parent)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            id_string = dialog.search.text()
            id_list = range_to_list(id_string)
            if self.opened_data.currentIndex() == 0:
                self.parent.model.find_cells(id_list)
            else:
                self.parent.signalmodel.filter_data(
                    self.opened_data_widget.currentRow(), id_list
                )

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
        layersToolBar.addAction(self.sumLayers)
        layersToolBar.addAction(self.subtractLayers)
        layersToolBar.addAction(self.intersectLayers)
        layersToolBar.addAction(self.toggleROIAction)
        layersToolBar.addAction(self.cropAction)
        layersToolBar.addAction(self.resetAxis)
        layersToolBar.addAction(self.alignImage)
        layersToolBar.addAction(self.cellSelect)
        layersToolBar.addAction(self.sendMask)
        layersToolBar.addAction(self.findIDs)

    def eventFilter(self, source, event):
        if (
            event.type() == QtCore.QEvent.ContextMenu
            and source is self.opened_layers_widget
        ):
            menu = QtWidgets.QMenu()

            renameAct = QAction("Change name", self)
            renameAct.setStatusTip("Open dialog to change current layer's name")
            renameAct.triggered.connect(self._setup_current_layer)
            menu.addAction(renameAct)

            removeAct = QAction("Remove", self)
            removeAct.setStatusTip("Removes the current layer")
            removeAct.triggered.connect(self._layer_remove)
            menu.addAction(removeAct)

            prefsAct = QAction("Preferences", self)
            prefsAct.setStatusTip("Preferences of the current layer")
            prefsAct.triggered.connect(self._layer_prefs)
            menu.addAction(prefsAct)
            menu.exec_(event.globalPos())

            return True

        elif (
            event.type() == QtCore.QEvent.ContextMenu
            and source is self.opened_data_widget
        ):
            idx = self.opened_data_widget.currentRow()
            menu = QtWidgets.QMenu()

            renameAct = QAction("Change name", self)
            renameAct.setStatusTip("Open dialog to change current dataset's name")
            renameAct.triggered.connect(self._setup_current_data)
            menu.addAction(renameAct)

            removeAct = QAction("Remove", self)
            removeAct.setStatusTip("Removes the current data")
            removeAct.triggered.connect(self._data_remove)
            menu.addAction(removeAct)

            tableAct = QAction("Show Table", self)
            tableAct.setStatusTip("Shows the data values as a table")
            self.tabViewer = TableViewer(self.parent.signalmodel, idx)
            tableAct.triggered.connect(self.tabViewer.display)
            menu.addAction(tableAct)
            menu.exec_(event.globalPos())

        return super(QWidget, self).eventFilter(source, event)

    def _tab_change(self, i):
        # Control disabling the buttons
        visibility = True
        if i == 1:
            visibility = False

        img_controls = [
            self.rotateAction,
            self.flipAction,
            self.sumLayers,
            self.subtractLayers,
            self.intersectLayers,
            self.toggleROIAction,
            self.cropAction,
            self.resetAxis,
            self.alignImage,
            self.cellSelect,
            self.sendMask,
        ]

        for control in img_controls:
            control.setEnabled(visibility)
            control.setVisible(visibility)


class QLayerWidget(QtWidgets.QListWidget):
    def __init__(self, gui=None, *args, **kwargs):
        super(QLayerWidget, self).__init__(*args, **kwargs)
        self.gui = gui

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Delete) and (
            self.gui.opened_data.currentIndex() == 0
        ):
            self.gui._layer_remove()
        else:
            super().keyPressEvent(event)


class QDataWidget(QtWidgets.QListWidget):
    def __init__(self, gui=None, *args, **kwargs):
        super(QDataWidget, self).__init__(*args, **kwargs)
        self.gui = gui

    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_Delete) and (
            self.gui.opened_data.currentIndex() == 1
        ):
            self.gui._data_remove()
        else:
            super().keyPressEvent(event)


class LayerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LayerDialog, self).__init__(parent)

        self.setWindowTitle("Layer selection")
        label = QtWidgets.QLabel("Second layer")
        self.combo = QtWidgets.QComboBox()
        self.parent = parent
        for i, name in enumerate(self.parent.model.list_images()):
            _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
            self.combo.addItem(_s_name, name)
            self.combo.setItemData(i, name, Qt.ToolTipRole)

        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(label, 0, 0)
        lay.addWidget(self.combo, 0, 1)
        lay.addWidget(box, 2, 0, 1, 2)


class TextDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TextDialog, self).__init__(parent)

        self.setWindowTitle("Find IDs")
        self.search_label = QLabel("IDs")
        self.hint = QLabel(
            "Write the IDs as regular expressions\nE.g.: 1-4,6 outputs 1 to 4, and 6."
        )
        self.search = QLineEdit()

        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(self.search_label, 0, 0)
        lay.addWidget(self.search, 0, 1)
        lay.addWidget(self.hint)
        lay.addWidget(box, 2, 0, 1, 2)


class LayerPrefsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, model=None, idx=None):
        super(LayerPrefsDialog, self).__init__(parent)

        self.model = model

        name = self.model.names[idx]
        sampling = self.model.samplingrate[idx]
        pixelsize = self.model.pixelsize[idx]
        scale = self.model.scales[idx][0]

        self.setWindowTitle("Preferences of {}".format(name))

        self.onlyDouble = QDoubleValidator()
        self.samplRate_label = QLabel("Sampling rate (Hz)")
        self.samplRate = QLineEdit()
        self.samplRate.setValidator(self.onlyDouble)
        self.samplRate.setText(str(sampling))

        self.onlyDouble = QDoubleValidator()
        self.pxSize_label = QLabel("Pixel size ({})".format(get_length()))
        self.pxSize = QLineEdit()
        self.pxSize.setValidator(self.onlyDouble)
        self.pxSize.setText(str(pixelsize))

        self.onlyDouble = QDoubleValidator()
        self.scaleSize_label = QLabel("Scale")
        self.scaleSize = QLineEdit()
        self.scaleSize.setValidator(self.onlyDouble)
        self.scaleSize.setText(str(scale))

        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(self.samplRate_label)
        lay.addWidget(self.samplRate)
        lay.addWidget(self.pxSize_label)
        lay.addWidget(self.pxSize)
        lay.addWidget(self.scaleSize_label)
        lay.addWidget(self.scaleSize)
        lay.addWidget(box)


class HorizontalTabBar(QtWidgets.QTabBar):
    def paintEvent(self, event):

        painter = QtWidgets.QStylePainter(self)
        option = QtWidgets.QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, option)
            painter.drawText(
                self.tabRect(index),
                QtCore.Qt.AlignCenter | QtCore.Qt.TextDontClip,
                self.tabText(index),
            )

    def tabSizeHint(self, index):
        size = QtWidgets.QTabBar.tabSizeHint(self, index)
        if size.width() < size.height():
            size.transpose()
        return size


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.setTabBar(HorizontalTabBar())
