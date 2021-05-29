from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QImage, QPixmap

# TODO: decide whether cv2 processing will go inside this class
import cv2
from utils.cmaps import cmaps

from model.inputdata import InputData

class ImageViewModel(QObject):
    newdata = pyqtSignal(str)
    removedata = pyqtSignal()
    updated = pyqtSignal()
    updatepos = pyqtSignal(float, float, int)

    def __init__(self, images=[], parent=None):
        self.images = images
        # TODO: make a new image class containing all 
        # information below (frames, opacities, colormap)
        self.frames = []
        self.opacities = []
        self.colormaps = []

        # TODO: treat these as properties
        self.maxframe = 0
        self.lastlayer = 0
        self.frame = 0
        self.curr_x = 0
        self.curr_y = 0
        super(ImageViewModel, self).__init__()

    @pyqtSlot()
    def load_image(self, file):
        self.lastlayer += 1
        image = InputData(file, memoryPersist=True)
        image.loadImage()
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(50)
        self.colormaps.append("bw")
        self.newdata.emit("Layer {}".format(self.lastlayer))

    @pyqtSlot()
    def add_image(self, data):
        image = InputData(data, memoryPersist=True)
        image.addImage()
        if self.maxframe < image.frames:
            self.maxframe = image.frames
        self.images.append(image)
        self.frames.append(image.frames)
        self.opacities.append(100)
        self.colormaps.append("bw")
        self.newdata.emit()

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
        background = cv2.normalize(
            _background, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )
        background = im_color = cv2.applyColorMap(background, cmaps[self.colormaps[0]])
        if len(self.images) > 1:
            for i in range(1, len(self.images)):
                frame = int(self.frame / (self.maxframe / self.frames[i]))
                _overlay = self.images[i]._image._imgs[frame]
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
    def set_colormap(self, cmap, index=0):
        self.colormaps[index] = cmap
        self.updated.emit()

    def get_opacity(self, index):
        return self.opacities[index]

    def get_colormap(self, index):
        return self.colormaps[index]

    # TODO: rewrite these methods as properties
    def get_frame(self, index):
        return self.frame

    def get_max_frame(self, index):
        return self.maxframe

    @pyqtSlot()
    def set_frame(self, t):
        self.frame = t
        self.updated.emit()
        self.updatepos.emit(self.curr_x, self.curr_y, self.frame)

    @pyqtSlot()
    def set_currpos(self, x, y):
        self.curr_x = x
        self.curr_y = y
        self.updatepos.emit(self.curr_x, self.curr_y, self.frame)

    # TODO: make it interactive and more efficient
    def get_icon(self, index):
        original = cv2.resize(self.images[index]._image._imgs[0],None,fx=0.2,fy=0.2)
        height, width = original.shape
        bytesPerLine = 3 * width
        icon_image = QImage(original.data, width, height, bytesPerLine, QImage.Format_RGB888)
        icon_pixmap = QPixmap.fromImage(icon_image)
        return icon_pixmap