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
import pyqtgraph as pg


class ImageViewPort(pg.ImageView):

    # constructor which inherit original
    # ImageView
    def __init__(self, model=None, parent=None, *args, **kwargs):
        pg.ImageView.__init__(self, *args, **kwargs)
        self.model = model
        self.parent = parent
        self.scene.sigMouseMoved.connect(self.mouse_moved)

        # This will hide some UI elements that will be handled by us
        self.ui.histogram.hide()
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        self.roi.rotatable = False

    # All functions below have similar code now, just as a placeholder
    def load_image(self, index):
        image = self.model.images[index]._image._imgs
        self.setImage(image)

    def update_viewport(self):
        image = self.model.get_current_view()
        self.setImage(image)

    def remove_image(self):
        image = self.model.get_current_view()
        self.setImage(image)

    def mouse_moved(self, event):
        scenePos = self.getImageItem().mapFromScene(event)
        row, col = int(scenePos.y()), int(scenePos.x())
        self.model.set_currpos(col, row)

    def roiChanged(self, event):
        roi_coord = [
            [event.pos().x(), event.pos().y()],
            [event.pos().x() + event.size().x(), event.pos().y() + event.size().y()],
        ]
        self.model.roi_coord = roi_coord

    def toggle_roi(self):
        if self.roi.isVisible():
            self.roi.hide()
        else:
            self.roi.show()
