#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import copy

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap

import cv2
import numpy as np

from camos.utils.cmaps import cmaps
from camos.model.inputdata import InputData


class ImageViewModel(QObject):
    newdata = pyqtSignal(str)
    removedata = pyqtSignal()
    updated = pyqtSignal()
    updatepos = pyqtSignal(float, float, int, int)
    updateint = pyqtSignal(int)

    def __init__(self, images=[], parent=None):
        self.images = images
        # TODO: make a new image class containing all
        # information below (frames, opacities, colormap)
        self.frames = []
        self.opacities = []
        self.contrasts = []
        self.brightnesses = []
        self.colormaps = []

        # TODO: treat these as properties
        self.maxframe = 0
        self.lastlayer = 0
        self.frame = 0
        self.curr_x = 0
        self.curr_y = 0
        self.roi_coord = [[0, 0], [1, 1]]

        # TODO: review this
        self.currentlayer = 0
        super(ImageViewModel, self).__init__()

    @pyqtSlot()
    def load_image(self, file):
        image = InputData(file, memoryPersist=True)
        image.loadImage()
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(50)
        self.brightnesses.append(0)
        self.contrasts.append(0)
        self.colormaps.append("bw")
        self.lastlayer += 1
        self.newdata.emit("Layer {}".format(self.lastlayer))

    @pyqtSlot()
    def add_image(self, image):
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(50)
        self.brightnesses.append(0)
        self.contrasts.append(0)
        self.colormaps.append("bw")
        self.lastlayer += 1
        self.newdata.emit("Layer {}".format(self.lastlayer))

    def crop_image(self, index):
        x_min, x_max = int(self.roi_coord[0][0]), int(self.roi_coord[1][0])
        y_min, y_max = int(self.roi_coord[0][1]), int(self.roi_coord[1][1])
        cropped = self.images[index]._image._imgs[:, x_min:x_max, y_min:y_max]
        image = copy.deepcopy(self.images[index])
        image._image._imgs = cropped
        image.crop = [0, 0, image._image._imgs[0].shape]
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(100)
        self.brightnesses.append(0)
        self.contrasts.append(0)
        self.colormaps.append("bw")
        self.lastlayer += 1
        self.newdata.emit("Layer {}".format(self.lastlayer))

    @pyqtSlot()
    def layer_remove(self, index):
        self.images.pop(index)
        self.frames.pop(index)
        self.opacities.pop(index)
        self.colormaps.pop(index)
        self.removedata.emit()

    def list_images(self):
        if len(self.images) == 0:
            return None
        return map(str, range(len(self.images)))

    def get_current_view(self, index=0):
        if len(self.images) == 0:
            return np.zeros((1, 1))
        # TODO: rewrite this.
        # Make access to images transparent, without _image and _imgs
        # New class from scratch (see comments in self.__init__ method)
        frame = int(self.frame / (self.maxframe / self.frames[0]))
        _background = self.images[0]._image._imgs[frame]
        _background = np.int16(_background)
        _background = (
            _background * (self.contrasts[0] / 127 + 1)
            - self.contrasts[0]
            + self.brightnesses[0]
        )
        background = cv2.normalize(
            _background, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )
        background = im_color = cv2.applyColorMap(background, cmaps[self.colormaps[0]])
        if len(self.images) > 1:
            for i in range(1, len(self.images)):
                frame = int(self.frame / (self.maxframe / self.frames[i]))
                _overlay = self.images[i]._image._imgs[frame]
                _overlay = np.int16(_overlay)
                _overlay = (
                    _overlay * (self.contrasts[i] / 127 + 1)
                    - self.contrasts[i]
                    + self.brightnesses[i]
                )
                _overlay = np.clip(_overlay, 0, 255)
                _overlay = np.uint8(_overlay)
                overlay = cv2.normalize(
                    _overlay, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
                )
                overlay = cv2.applyColorMap(overlay, cmaps[self.colormaps[i]])
                background = cv2.addWeighted(
                    background, 1, overlay, self.opacities[i] / 100, 0, dtype=cv2.CV_64F
                )
        return background

    @pyqtSlot()
    def set_opacity(self, opacity, index=0):
        self.opacities[index] = opacity
        self.updated.emit()

    @pyqtSlot()
    def rotate_image(self, index=0):
        rotated = np.rot90(self.images[index]._image._imgs, axes=(1, 2))
        self.images[index]._image._imgs = rotated
        self.images[index].crop = [0, 0, rotated[0].shape]
        self.updated.emit()

    @pyqtSlot()
    def duplicate_image(self, index=0):
        image = copy.deepcopy(self.images[index])
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(50)
        self.brightnesses.append(0)
        self.contrasts.append(0)
        self.colormaps.append("bw")
        self.lastlayer += 1
        self.newdata.emit("Layer {}".format(self.lastlayer))

    @pyqtSlot()
    def set_contrast(self, contrast, index=0):
        self.contrasts[index] = contrast
        self.updated.emit()

    @pyqtSlot()
    def set_brightness(self, brightness, index=0):
        self.brightnesses[index] = brightness
        self.updated.emit()

    @pyqtSlot()
    def set_colormap(self, cmap, index=0):
        self.colormaps[index] = cmap
        self.updated.emit()

    def get_opacity(self, index=0):
        return self.opacities[index]

    def get_colormap(self, index=0):
        return self.colormaps[index]

    def get_brightness(self, index=0):
        return self.brightnesses[index]

    def get_contrast(self, index=0):
        return self.contrasts[index]

    # TODO: rewrite these methods as properties
    def get_frame(self, index):
        return self.frame

    def get_max_frame(self, index):
        return self.maxframe

    @pyqtSlot()
    def set_frame(self, t):
        self.frame = t
        self.updated.emit()
        self.updatepos.emit(self.curr_x, self.curr_y, self.frame, self.get_currint())

    @pyqtSlot()
    def set_currpos(self, x, y):
        self.curr_x = x
        self.curr_y = y
        self.updatepos.emit(self.curr_x, self.curr_y, self.frame, self.get_currint())

    def get_currint(self):
        try:
            frame = int(self.frame / (self.maxframe / self.frames[self.currentlayer]))
            return self.images[self.currentlayer]._image._imgs[
                frame, self.curr_x, self.curr_y
            ]
        except:
            pass

    # TODO: make it interactive and more efficient
    def get_icon(self, index):
        original = cv2.resize(self.images[index]._image._imgs[0], None, fx=0.2, fy=0.2)
        height, width = original.shape
        bytesPerLine = 3 * width
        icon_image = QImage(
            original.data, width, height, bytesPerLine, QImage.Format_RGB888
        )
        icon_pixmap = QPixmap.fromImage(icon_image)
        return icon_pixmap
