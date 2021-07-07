# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
import camos.model.image as img


class InputData:
    """The InputData object.
    This behaves as a container for the data, as a numpy array, and the main
    properties of interest for the object to be handled in visualization and analysis.
    """

    def __init__(self, file=None, memoryPersist=False, name="New Layer"):
        """Initialization of the object

        Args:
            file ([str, numpy.ndarray], optional): Can be a numpy array containing any numeric data, or a path to a file. The opening plugin must support this. Defaults to None.
            memoryPersist (bool, optional): whether the data must be loaded into memory, at once, or can be loaded as required, from disk. Defaults to False.
            stack (bool): the file bust be interpreted as a stack (False), various files
                are interpreted as a single stack (True)
        """
        self.file = file
        self.name = name
        self._image = None
        self.frames = 0
        self.data = None
        self.memoryPersist = memoryPersist
        self.max = 0
        self.opacity = 50
        self.brightness = 0
        self.contrast = 0
        self.colormap = "gray"

    def image(self, index):
        """Returns the current frame for an image

        Args:
            index (int): index corresponding to the frame

        Returns:
            np.ndarray: current frame of the image, with shape (height, width, channels)
        """
        return self._image[index]

    def loadImage(self):
        # TODO: load all into memory?
        if self.memoryPersist:
            self._image = img.Stack(self.file, dx=1, dz=1, units="nm")
        else:
            pass

        self.frames = len(self._image)
        self.max = self._image._imgs.max()
