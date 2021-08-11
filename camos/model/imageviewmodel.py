# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtWidgets

import copy
import numpy as np

from camos.model.inputdata import InputData

MAXHISTORY = 20
MAXNAMELEN = 300


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

    # For data being updated, layer number
    updatedscale = pyqtSignal(float)

    # For positions being updated
    updatepos = pyqtSignal(float, float, int, int, float)

    # For intensities being updated
    updateint = pyqtSignal(int)

    # For communicating to plots being updated
    # imagetoplot = pyqtSignal(list)

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
        self.translation = []
        self.scales = []
        self.samplingrate = []
        self.pixelsize = []
        self.properties = []

        self.maxframe = 0
        self.frame = 0
        self.curr_x = 0
        self.curr_y = 0
        self._currentlayer = 0
        self.roi_coord = [[0, 0], [1, 1]]

        self.undoHistory = []

        # Initialize the parent QObject class
        super(ImageViewModel, self).__init__()

    @property
    def currentlayer(self):
        return self._currentlayer

    @currentlayer.setter
    def currentlayer(self, value):
        self._currentlayer = value
        try:
            pxs = self.pixelsize[value]
            self.update_scale(pxsize=pxs)
        except:
            pass

    @pyqtSlot()
    def add_image(
        self,
        image,
        name=None,
        cmap="gray",
        scale=[1, 1],
        translation=[0, 0],
        samplingrate=1,
        properties={},
        opacity=50,
    ):
        """Any image, once it has been loaded within a InputData object, can be loaded onto the ImageViewModel through this function. It will read all the features for the loaded image, and recalculate the global (shared) features (maximum number of frames overall, ROIs...)

        Args:
            image (InputData): the instance of InputData object to be appended to self.images; represents a image
        """
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(opacity)
        self.brightnesses.append(0)
        self.contrasts.append(1)
        self.colormaps.append(cmap)
        self.properties.append(properties)

        if name == None:
            name = "Layer {}".format(len(self.images) - 1)

        if name in self.names or name == "":
            name = "New_{}_{}".format(name, len(self.names))

        if len(name) > MAXNAMELEN:
            name = name[0:MAXNAMELEN]

        self.names.append(name)
        self.translation.append(translation)
        self.scales.append(scale)
        self.samplingrate.append(samplingrate)
        self.pixelsize.append(image._image.dx)
        self.newdata.emit(-1)

    def crop_image(self, index):
        """Crops the image contained in this model for which the index is provided

        Args:
            index (int): position of the InputData object containing the image, in the list self.images
        """
        scale = self.scales[index]
        x_tr, y_tr = self.translation[index]
        y_shape_max, x_shape_max = self.images[index]._image._imgs.shape[1:3]
        y_min, y_max = (
            int(max(0, abs(int(y_tr - self.roi_coord[0][0])) / scale[1])),
            int(min(y_shape_max, abs(int(y_tr - self.roi_coord[1][0])) / scale[1])),
        )
        x_min, x_max = (
            int(max(0, abs(int(x_tr - self.roi_coord[0][1])) / scale[0])),
            int(min(x_shape_max, abs(int(x_tr - self.roi_coord[1][1])) / scale[0])),
        )

        cropped = self.images[index]._image._imgs[:, y_min:y_max, x_min:x_max]
        image = InputData(cropped, name="Cropped from Layer {}".format(index),)
        image.loadImage()
        self.add_image(image, "Cropped from Layer {}".format(index), scale=scale)

    def flip_image(self, index):
        """Horizontally flips the image contained in this model for which the index is provided

        Args:
            index (int): position of the InputData object containing the image, in the list self.images
        """
        scale = self.scales[index]
        flipped = np.flip(self.images[index]._image._imgs, axis=2)
        image = InputData(flipped, name="Flipped from Layer {}".format(index),)
        image.loadImage()
        self.add_image(image, "Flipped from Layer {}".format(index), scale=scale)

    def select_cells(self, cell_ID=None, scale=[1, 1]):
        """Selects the cells in the currently selected layer if cell selection is enabled. See the method self.trigger_select_cells
        """
        mask = self.images[self.currentlayer]._image._imgs[0]
        if cell_ID == None:
            x, y = self.curr_x, self.curr_y
            cell_ID = mask[x, y]
        else:
            cell_ID = int(cell_ID[2])
        cell = np.where(mask == cell_ID, mask, 0)
        image = InputData(cell, name="Selected Cell {}".format(cell_ID))
        image.loadImage()
        scale = self.scales[self.currentlayer]
        self.add_image(
            image,
            "Cell {} from Layer {}".format(cell_ID, self.currentlayer),
            scale=scale,
        )

    def find_cells(self, cell_ID=[0]):
        """Selects the cells in the currently selected layer if cell selection is enabled. See the method self.trigger_select_cells
        """
        mask = self.images[self.currentlayer].image(0)
        cell_ID = list(map(int, cell_ID))
        ids = np.isin(mask, cell_ID)
        found = np.where(ids == True, mask, 0)
        newname = "Cells {} from Layer {}".format(cell_ID, self.currentlayer)
        image = InputData(found, name=newname)
        image.loadImage()
        scale = self.scales[self.currentlayer]
        self.add_image(
            image, newname, scale=scale,
        )

    def filter_layer(self, lowerf, upperf):
        """Filters the cells in the currently selected layer, between lower and upper values.
        """
        mask = self.images[self.currentlayer].image(0)
        found = np.where((mask > lowerf) & (mask < upperf), mask, 0)
        newname = "Filtered from Layer {}".format(self.currentlayer)
        image = InputData(found, name=newname)
        image.loadImage()
        scale = self.scales[self.currentlayer]
        self.add_image(
            image, newname, scale=scale,
        )

    def update_plots(self, layer=None):
        if layer == None:
            idx = [self.get_currint()]
        else:
            idx = np.unique(self.images[self.currentlayer]._image._imgs[0]).tolist()
        return idx

    @pyqtSlot()
    def update_prefs(self, layer=None, sampling=1, pxsize=1, scale=1):
        self.samplingrate[layer] = sampling
        self.pixelsize[layer] = pxsize
        self.scales[layer] = [scale, scale]
        self.update_scale(pxsize)
        self.updated.emit(layer)

    def update_scale(self, pxsize=1):
        self.updatedscale.emit(pxsize)

    @pyqtSlot()
    def layer_remove(self, index):
        """Given an index, removes the InputData object from the self.images list, and all the metadata linked to that same index

        Args:
            index (int): position of the image in the self.images list
        """
        assert index != None

        # Correct the current layer index
        if index == len(self.images) - 1:
            self.currentlayer -= 1
        elif index < self.currentlayer:
            self.currentlayer -= 1

        # Prevent the index being negative
        if self.currentlayer < 0:
            self.currentlayer = 0

        # Remove all data and properties linked to index
        self.images.pop(index)
        self.frames.pop(index)
        self.opacities.pop(index)
        self.colormaps.pop(index)
        self.names.pop(index)
        self.translation.pop(index)
        self.scales.pop(index)
        self.viewitems.pop(index)
        self.properties.pop(index)
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

        return _img

    @pyqtSlot()
    def rotate_image(self, index=0, undo=None):
        """Performs a counter-clockwise rotation on the selected layer (image)

        Args:
            index (int, optional): layer to configure. Defaults to 0.
        """
        rotated = np.rot90(self.images[index]._image._imgs, axes=(1, 2))
        self.images[index]._image._imgs = rotated
        self.images[index].crop = [0, 0, rotated[0].shape]
        self.updatedframe.emit(index)

    def reset_position(self, index=0, undo=None):
        if undo is not None:
            index = undo["index"]
            position = undo["position"]
        else:
            position = (0, 0)

        # Apply the translation
        self.translate_position(index, position, undo=undo)

    @pyqtSlot()
    def translate_position(self, index=0, position=(0, 0), undo=None):
        if undo is not None:
            index = undo["index"]
            position = undo["position"]

        if undo is None:
            # Create the undo command
            _undo = [
                {
                    "function": self.translate_position,
                    "index": index,
                    "position": (
                        self.translation[index][0],
                        self.translation[index][1],
                    ),
                }
            ]

            # Add to the undo queue
            self.undoAdd(_undo)

        # Apply the translation
        self.axes.emit(index, position)

    def align_layers(self, layer=0, undo=None):
        if undo is not None:
            curr = undo["curr"]
            delta_x = undo["delta_x"]
            delta_y = undo["delta_y"]
            layer = undo["layer"]
        else:
            curr = self.currentlayer
            delta_x = self.translation[curr][0]
            delta_y = self.translation[curr][1]

        # Apply the translation
        self.translate_position(layer, (delta_x, delta_y))

        if undo is None:
            # Create the undo command
            _undo = [
                {
                    "function": self.align_layers,
                    "layer": layer,
                    "curr": curr,
                    "delta_x": -delta_x,
                    "delta_y": -delta_y,
                }
            ]

            # Add to the undo queue
            self.undoAdd(_undo)

    def sum_layers(self, layer=0):
        curr = self.currentlayer
        a = self.images[curr].image(0)
        b = self.images[layer].image(0)
        assert a.shape == b.shape

        summed = a + b
        image = InputData(
            summed,
            name="Sum from {} and {}".format(self.names[layer], self.names[curr]),
        )
        image.loadImage()
        self.add_image(
            image, "Sum from {} and {}".format(self.names[layer], self.names[curr])
        )

    def subtract_layers(self, layer=0):
        curr = self.currentlayer
        a = self.images[curr].image(0)
        b = self.images[layer].image(0)
        assert a.shape == b.shape

        subtracted = np.abs(a - b)
        image = InputData(
            subtracted,
            name="Subtract from {} and {}".format(self.names[layer], self.names[curr]),
        )
        image.loadImage()
        self.add_image(
            image, "Subtract from {} and {}".format(self.names[layer], self.names[curr])
        )

    def intersect_layers(self, layer=0):
        curr = self.currentlayer
        a = self.images[curr].image(0)
        b = self.images[layer].image(0)
        assert a.shape == b.shape

        multiplied = np.multiply(a, b)
        intersect = np.where(multiplied != 0, a, 0)
        image = InputData(
            intersect,
            name="Intersect from {} and {}".format(self.names[layer], self.names[curr]),
        )
        image.loadImage()
        self.add_image(
            image,
            "Intersect from {} and {}".format(self.names[layer], self.names[curr]),
        )

    @pyqtSlot()
    def duplicate_image(self, index=0):
        """Duplicates the current layer, by copying the InputData object, and calls the self.add_image method.

        Args:
            index (int, optional): index of the layer to duplicate, according to self.images. Defaults to 0.
        """
        image = copy.deepcopy(self.images[index])
        self.add_image(image, "Duplicate of Layer {}".format(index))

    @pyqtSlot()
    def set_values(self, opacity=1, cmap="grey", index=0, undo=None):
        """Configures the properties for the selected layer; emits an event, i.e., so the ViewPort knows that it has to call the self.get_current_view method.

        Args:
            cmap (cv2.ColormapTypes): colormap to be applied to the image
            index (int, optional): index of the image in the self.images list. Defaults to 0.
        """
        if undo is not None:
            index = undo["index"]
            opacity = undo["opacity"]
            cmap = undo["cmap"]

        if undo is None:
            # Create the undo command
            _undo = [
                {
                    "function": self.set_values,
                    "index": index,
                    "opacity": self.opacities[index],
                    "cmap": self.colormaps[index],
                }
            ]

            # Add to the undo queue
            self.undoAdd(_undo)

        # Apply the transformation
        self.opacities[index] = opacity
        self.colormaps[index] = cmap
        self.updated.emit(index)

    def set_translation(self, index, x, y):
        # Create the undo command
        # Will apply the translate position to
        # reverse setting the translation
        _undo = [
            {
                "function": self.translate_position,
                "index": index,
                "position": (self.translation[index][0], self.translation[index][1]),
            }
        ]

        # Add to the undo queue
        self.undoAdd(_undo)

        # Store the translation
        self.translation[index] = (x, y)

    def get_opacity(self, index=0):
        return self.opacities[index]

    def get_colormap(self, index=0):
        return self.colormaps[index]

    def get_brightness(self, index=0):
        return self.brightnesses[index]

    def get_contrast(self, index=0):
        return self.contrasts[index]

    def get_scale(self, index=0):
        return self.scales[index][0]

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
        assert len(self.images) > 0
        self.frame = t
        self.updatedframe.emit(self.currentlayer)
        pxs = self.pixelsize[self.currentlayer]
        self.updatepos.emit(
            self.curr_x, self.curr_y, self.frame, self.get_currint(), pxs
        )

    @pyqtSlot()
    def set_currpos(self, x, y):
        """Once a position has been selected or hovered on the image, this emits an event, i.e., so the UI can be updated.

        Args:
            x (int): X-coordinate of the current selected layer, by index
            y (int): Y-coordinate of the current selected layer, by index
        """
        try:
            self.curr_x = x
            self.curr_y = y
            pxs = self.pixelsize[self.currentlayer]
            self.updatepos.emit(
                self.curr_x, self.curr_y, self.frame, self.get_currint(), pxs
            )
        except:
            pass

    def get_currint(self):
        try:
            if (self.curr_x < 0) or (self.curr_y < 0):
                return 0
            frame = int(self.frame / (self.maxframe / self.frames[self.currentlayer]))
            return self.images[self.currentlayer]._image._imgs[
                frame, self.curr_x, self.curr_y
            ]
        except:
            return 0

    def get_icon(self, index):
        """This creates an icon for the corresponding layer

        Args:
            index (int): index of the image in the self.images list

        Returns:
            QPixmap: icon that has been generated as a thumbnail of the input layer
        """
        try:
            from PIL import Image

            original = (
                Image.fromarray(self.images[index].image(0).astype(np.uint8))
                .convert("RGB")
                .resize((128, 128))
            )
            height, width = original.size
            bytesPerLine = 3 * width
            icon_image = QImage(
                np.array(original), width, height, bytesPerLine, QImage.Format_RGB888
            )
            icon_pixmap = QPixmap.fromImage(icon_image)
        except:
            icon_pixmap = QPixmap()
        return icon_pixmap

    def undoAdd(self, _undo):
        self.undoHistory.append(_undo)
        if len(self.undoHistory) > MAXHISTORY:
            self.undoHistory.pop(0)

    def undoLastAction(self):
        assert len(self.undoHistory) > 0, "Nothing to undo"

        self.undoHistory[-1][0]["function"](undo=self.undoHistory[-1][0])
        self.undoHistory.pop(-1)

    def from_clipboard(self):
        try:
            _qimage = QtWidgets.QApplication.clipboard().image()
            im = self.convertQImageToMat(_qimage)

            image = InputData(im, name="Image from Clipboard")
            image.loadImage()
            self.add_image(image, name="Image from Clipboard")
        except Exception as e:
            raise ValueError("Could not paste image")

    def convertQImageToMat(self, incomingImage):
        """  Converts a QImage into an opencv MAT format  """

        incomingImage = incomingImage.convertToFormat(3)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        if incomingImage.byteCount() == width * height:
            arr = np.array(ptr).reshape(height, width, 1)
        else:
            arr = np.array(ptr).reshape(height, width, 3)
        return arr

    def to_clipboard(self):
        try:
            from PIL import Image

            original = Image.fromarray(self.images[self.currentlayer].image(0)).convert(
                "RGB"
            )
            height, width, channel = np.array(original).shape
            bytesPerLine = 3 * width
            qImg = QImage(
                np.array(original), width, height, bytesPerLine, QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qImg)
            QtWidgets.QApplication.clipboard().setPixmap(pixmap)
        except Exception as e:
            raise ValueError("Could not copy image")

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["viewitems"]
        return state

    def __setstate__(self, d):
        self.__dict__ = d
