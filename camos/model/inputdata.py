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