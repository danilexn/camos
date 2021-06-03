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