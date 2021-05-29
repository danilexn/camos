from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

class SignalViewModel(QObject):
    newdata = pyqtSignal()

    def __init__(self, data=[], parent=None):
        self.data = data
        self.parent = parent
        super(SignalViewModel, self).__init__()

    @pyqtSlot()
    def add_data(self, data):
        self.data.append(data)
        self.newdata.emit()