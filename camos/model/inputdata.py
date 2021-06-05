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
import numpy as np
import multipagetiff as tiff


class InputData:
    def __init__(self, file=None, type=None, memoryPersist=False):
        self.file = file
        self._image = None
        self.frames = 0
        self.data = None
        self.memoryPersist = memoryPersist
        self.max = 0
        self.opacity = 50
        self.brightness = 0
        self.contrast = 0
        self.colormap = "bw"

    def image(self, index):
        return self._image[index]

    def loadImage(self):
        # TODO: load all into memory?
        # Make a setting for maximum memory usage
        if self.memoryPersist:
            # TODO: reduce the dependency from multipagetiff
            # WARNING: adapt the imageviewmodel if multipagetiff is not used anymore
            self._image = tiff.Stack(self.file, dx=1, dz=1, units="nm")
        else:
            pass

        self.frames = len(self._image)
        self.max = self._image._imgs.max()

    def addImage(self):
        self._image = tiff.Stack(self.file, dx=1, dz=1, units="nm")
        self.frames = len(self._image)
        self.max = self._image._imgs.max()

    def loadData(self):
        # TODO: we could include the reference to the hdf5 reader here
        self.data = np.random.random((64, 64))
