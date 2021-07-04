# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.saving import Saving

from PIL import Image


class SaveImage(Saving):
    analysis_name = "Save Image"

    def __init__(self, *args, **kwargs):
        super(SaveImage, self).__init__(extensions="tif File (*.tif)", *args, **kwargs)

    def _run(self):
        currentlayer = self.model.currentlayer
        self.image = self.model.images[currentlayer]._image._imgs
        shape = self.image.shape
        pxs = self.model.pixelsize[currentlayer]
        if shape[0] == 1:
            im = Image.fromarray(self.image[0])
            im.save(self.filename, dpi=(pxs, pxs))
        else:
            imlist = []
            for m in self.image:
                imlist.append(Image.fromarray(m))

            imlist[0].save(
                self.filename,
                compression="tiff_deflate",
                save_all=True,
                append_images=imlist[1:],
                dpi=(pxs, pxs),
            )
