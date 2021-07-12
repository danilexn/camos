# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

# Derived from multipagetiff, credits to mpascucci

from tempfile import mkdtemp
import os.path as _path

from collections.abc import Sequence
from PIL import Image
import numpy as np

import copy


def tiff2nparray(path, persistence=True):
    im = Image.open(path)
    i = 0
    frames = []
    try:
        while True:
            im.seek(i)
            frames.append(np.array(im))
            i += 1
    except EOFError:
        pass

    frames = np.array(frames)
    if persistence:
        return frames, im.info

    out_mmap = np.memmap(
        _path.join(mkdtemp(), "memmap.dat"),
        dtype=frames.dtype,
        mode="w+",
        shape=frames.shape,
    )

    out_mmap[:] = frames
    return out_mmap, im.info


def list2stack(paths, persistence=True):
    frames = []
    for path in paths:
        im = Image.open(path)
        i = 0
        try:
            while True:
                im.seek(i)
                frames.append(np.array(im))
                i += 1
        except EOFError:
            pass

    frames = np.array(frames)
    if persistence:
        return frames, im.info

    out_mmap = np.memmap(
        _path.join(mkdtemp(), "memmap.dat"),
        dtype=frames.dtype,
        mode="w+",
        shape=frames.shape,
    )
    out_mmap[:] = frames

    return out_mmap, im.info


def nparray(arr, persistence=True):
    i = 0
    frames = []
    try:
        while True:
            if len(arr.shape) == 3:
                if (arr.shape[2]) <= 3:
                    frames.append(np.array(arr))
                    break
                frames.append(np.array(arr[i, :, :]))
                i += 1
            elif len(arr.shape) == 2:
                frames.append(np.array(arr[:, :]))
                break
            elif len(arr.shape) == 4:
                frames.append(np.array(arr[i, :, :, :]))
                i += 1
            else:
                raise NotImplementedError("Image shape is not valid")
    except:
        pass

    frames = np.array(frames)
    if persistence:
        return frames

    out_mmap = np.memmap(
        _path.join(mkdtemp(), "memmap.dat"),
        dtype=frames.dtype,
        mode="w+",
        shape=frames.shape,
    )
    out_mmap[:] = frames

    return out_mmap


class Stack(Sequence):
    """The multipage tiff object.
    it behaves as a list which members are the pages of the tiff.
    Each page is a numpy array.
    """

    def __init__(
        self, path, dx, dz, title="", z_label="depth", units="", persistence=True
    ):
        """
        :param path: path to the tiff file
        :param dx: value of one pixel in physical units, on the transverse plane (X,Y)
        :param dz: value of one pixel in physical units, on the axial direction (Z)
        :param units: physical units of the z axis
        :param z_label: label used for the color coding
        :param cmap: colormap used to repsresent the
        :param title:
        properties:
        these properties can be modified
        - crop: [x0,y0,x1,y1] defines a rectangle which crops the stack when plotting
        - start_frame, end_frame : int, defines the first and last frame to use
        - keyframe: the frame at which z=0
        """
        self.dx = dx
        self.dz = dz
        if type(path) == str:
            self._imgs, info = tiff2nparray(path, persistence)
            try:
                self.dx = info["resolution"][0]
            except:
                pass
        elif type(path) == list:
            self._imgs, info = list2stack(path, persistence)
        elif type(path) == np.ndarray:
            self._imgs = nparray(copy.deepcopy(path), persistence)
        else:
            raise NotImplementedError("The path format is unknown")

        self.crop = [0, 0, *self._imgs[0].shape]
        self.keyframe = len(self) // 2
        self.start_frame = 0
        self.end_frame = len(self) - 1
        self.title = title
        self.units = units
        self.z_label = z_label
        self.coords = []

    def reverse(self):
        self._imgs = self.pages[::-1]
        self.start_frame = len(self) - self.end_frame
        self.end_frame = len(self) - self.start_frame

    def reduce(self, f=2):
        self._imgs = self.pages[::f]
        self.dz *= 2
        self.keyframe = round(self.keyframe // f)
        self.start_frame = round(self.start_frame // f)
        self.end_frame = round(self.end_frame // f)

    def __getitem__(self, i):
        return self.pages[i]

    def __len__(self):
        return self.pages.shape[0]

    def set_start_in_units(self, start):
        self.start_frame = self.keyframe + round(start // self.dz) + 1

    def set_end_in_units(self, end):
        self.end_frame = self.keyframe + round(end // self.dz)

    @property
    def pages(self):
        x, y, h, w = self.crop[0:4]
        return self._imgs[:, x : x + h, y : y + w]

    @property
    def selection_length(self):
        return self.end_frame - self.start_frame + 1

    @property
    def range_in_units(self):
        return (
            np.array(
                [self.start_frame - self.keyframe, self.end_frame - self.keyframe,]
            )
            * self.dz
        )
