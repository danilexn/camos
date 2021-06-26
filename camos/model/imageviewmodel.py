# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import copy
from operator import le

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap

import cv2
import numpy as np

from camos.utils.cmaps import cmaps
from camos.model.inputdata import InputData


class ImageViewModel(QObject):
    """The ImageViewModel object. This contains information regarding image data, without considering format.
    Images are stored in self.images as InputData objects. They are accessible by index, which corresponds to the rest of
    properties, such as self.frames, self.opacities...

    This class also handles the basic modifications of the images before they are sent to the ViewPort.

    Args:
        QObject: inherit a parent PyQt5 QObject class
    """

    # Signals that the class emits

    # For new image (data) being added
    newdata = pyqtSignal(int)

    # For axis being reset
    axes = pyqtSignal(int, tuple)

    # For data being removed
    removedata = pyqtSignal(int)

    # For data being updated, layer number
    updated = pyqtSignal(int)

    # For data being updated, layer number
    updatedframe = pyqtSignal(int)

    # For positions being updated
    updatepos = pyqtSignal(float, float, int, int)

    # For intensities being updated
    updateint = pyqtSignal(int)

    def __init__(self, images=[], parent=None):
        """Initialization of the class

        Args:
            images (list, optional): this can be passed from any list of InputData objects. Defaults to [].
            parent (QMainWindow, optional): the parent PyQt5 object from which the model is created, so the model can interact with the UI. Defaults to None.
        """
        self.images = images

        self.frames = []
        self.opacities = []
        self.contrasts = []
        self.brightnesses = []
        self.colormaps = []
        self.names = []
        self.viewitems = []

        self.maxframe = 0
        self.frame = 0
        self.curr_x = 0
        self.curr_y = 0
        self.roi_coord = [[0, 0], [1, 1]]

        self.currentlayer = 0
        self._enable_select_cells = False

        # Initialize the parent QObject class
        super(ImageViewModel, self).__init__()

    @pyqtSlot()
    def add_image(self, image, name = None, cmap = "gray"):
        """Any image, once it has been loaded within a InputData object, can be loaded onto the ImageViewModel through this function. It will read all the features for the loaded image, and recalculate the global (shared) features (maximum number of frames overall, ROIs...)

        Args:
            image (InputData): the instance of InputData object to be appended to self.images; represents a image
        """
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(50)
        self.brightnesses.append(0)
        self.contrasts.append(0)
        self.colormaps.append(cmap)

        if name == None:
            name = "Layer {}".format(len(self.images) - 1)

        self.names.append(name)
        self.newdata.emit(-1)

    def crop_image(self, index):
        """Crops the image contained in this model for which the index is provided

        Args:
            index (int): position of the InputData object containing the image, in the list self.images
        """
        x_min, x_max = int(self.roi_coord[0][0]), int(self.roi_coord[1][0])
        y_min, y_max = int(self.roi_coord[0][1]), int(self.roi_coord[1][1])
        cropped = self.images[index]._image._imgs[:, x_min:x_max, y_min:y_max]
        image = InputData(
            cropped,
            memoryPersist=True,
            name="Cropped from Layer {}".format(index),
        )
        image.loadImage()
        self.add_image(image, "Cropped from Layer {}".format(index))

    def trigger_select_cells(self):
        """Toggles on or off the selection of cells in the current layer after a "double click" mouse event
        """
        self._enable_select_cells = (
            False if self._enable_select_cells else True
        )

    def select_cells(self):
        """Selects the cells in the currently selected layer if cell selection is enabled. See the method self.trigger_select_cells
        """
        if not self._enable_select_cells:
            return
        x, y = self.curr_x, self.curr_y
        mask = self.images[self.currentlayer]._image._imgs[0]
        cell_ID = mask[x, y]
        cell = np.where(mask == cell_ID, mask, 0)
        image = InputData(
            cell, memoryPersist=True, name="Selected Cell {}".format(cell_ID)
        )
        image.loadImage()
        self.add_image(image, "Cell {} from Layer {}".format(cell_ID, self.currentlayer))

    @pyqtSlot()
    def layer_remove(self, index):
        """Given an index, removes the InputData object from the self.images list, and all the metadata linked to that same index

        Args:
            index (int): position of the image in the self.images list
        """
        assert index != None
        self.images.pop(index)
        self.frames.pop(index)
        self.opacities.pop(index)
        self.colormaps.pop(index)
        self.names.pop(index)
        self.removedata.emit(index)

    def list_images(self):
        """Gives a list of strings containing the names of the images loaded into this model

        Returns:
            list: list containing the names of the images, as str
        """
        if len(self.images) == 0:
            return None
        return self.names

    def get_layer(self, layer=0):
        """This function generates the visualization of the indicated layer in the model, according to its properties (colormap, opacity...).

        Returns:
            np.ndarray: the merge of all layers in the model
        """
        if len(self.images) == 0:
            return np.zeros((1, 1))
        _frame = int(self.frame / (self.maxframe / self.frames[layer]))
        _img = self.images[layer]._image._imgs[_frame]
        #_img = np.int16(_img)
        #_img = (
        #    _img * (self.contrasts[layer] / 127 + 1)
        #    - self.contrasts[layer]
        #    + self.brightnesses[layer]
        #)
        #_img = cv2.normalize(
        #    _img, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
        #)
        #_img =  cv2.applyColorMap(
        #    _img, cmaps[self.colormaps[layer]]
        #)

        #b, g, r = cv2.split(_img)
        #a = np.ones(b.shape, dtype=b.dtype) * self.opacities[layer]

        #img = cv2.merge((b, g, r, a))
        return _img

    @pyqtSlot()
    def rotate_image(self, index=0):
        """Performs a counter-clockwise rotation on the selected layer (image)

        Args:
            index (int, optional): layer to configure. Defaults to 0.
        """
        rotated = np.rot90(self.images[index]._image._imgs, axes=(1, 2))
        self.images[index]._image._imgs = rotated
        self.images[index].crop = [0, 0, rotated[0].shape]
        self.updatedframe.emit(index)

    def reset_position(self, index=0):
        self.translate_position(index, (0, 0))

    @pyqtSlot()
    def translate_position(self, index=0, position=(0, 0)):
        self.axes.emit(index, position)

    @pyqtSlot()
    def duplicate_image(self, index=0):
        """Duplicates the current layer, by copying the InputData object, and calls the self.add_image method.

        Args:
            index (int, optional): index of the layer to duplicate, according to self.images. Defaults to 0.
        """
        image = copy.deepcopy(self.images[index])
        self.add_image(image, "Duplicate of Layer {}".format(index))

    @pyqtSlot()
    def set_values(self, opacity, brightness, contrast, cmap, index=0):
        """Configures the properties for the selected layer; emits an event, i.e., so the ViewPort knows that it has to call the self.get_current_view method.

        Args:
            cmap (cv2.ColormapTypes): colormap to be applied to the image
            index (int, optional): index of the image in the self.images list. Defaults to 0.
        """
        self.opacities[index] = opacity
        self.brightnesses[index] = brightness
        self.contrasts[index] = contrast
        self.colormaps[index] = cmap
        self.updated.emit(index)

    def get_opacity(self, index=0):
        return self.opacities[index]

    def get_colormap(self, index=0):
        return self.colormaps[index]

    def get_brightness(self, index=0):
        return self.brightnesses[index]

    def get_contrast(self, index=0):
        return self.contrasts[index]

    def get_frame(self, index):
        return self.frame

    def get_max_frame(self, index):
        return self.maxframe

    @pyqtSlot()
    def set_frame(self, t):
        """Once a frame has been configured in the model, this emits an event so it can be handled, i.e., by the UI to update the statusbar.

        Args:
            t (int): number of the frame to be configured
        """
        self.frame = t
        self.updatedframe.emit(self.currentlayer)
        self.updatepos.emit(
            self.curr_x, self.curr_y, self.frame, self.get_currint()
        )

    @pyqtSlot()
    def set_currpos(self, x, y):
        """Once a position has been selected or hovered on the image, this emits an event, i.e., so the UI can be updated.

        Args:
            x (int): X-coordinate of the current selected layer, by index
            y (int): Y-coordinate of the current selected layer, by index
        """
        self.curr_x = x
        self.curr_y = y
        self.updatepos.emit(
            self.curr_x, self.curr_y, self.frame, self.get_currint()
        )

    def get_currint(self):
        try:
            frame = int(
                self.frame / (self.maxframe / self.frames[self.currentlayer])
            )
            return self.images[self.currentlayer]._image._imgs[
                frame, self.curr_x, self.curr_y
            ]
        except:
            pass

    def get_icon(self, index):
        """This creates an icon for the corresponding layer

        Args:
            index (int): index of the image in the self.images list

        Returns:
            QPixmap: icon that has been generated as a thumbnail of the input layer
        """
        try:
            original = cv2.resize(
                self.images[index]._image._imgs[0], (50, 50)
            )
            height, width = original.shape
            bytesPerLine = 3 * width
            icon_image = QImage(
                original.data, width, height, bytesPerLine, QImage.Format_RGB888
            )
            icon_pixmap = QPixmap.fromImage(icon_image)
        except:
            icon_pixmap = QPixmap()
        return icon_pixmap

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d
