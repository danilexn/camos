from PyQt5 import QtWidgets

class ErrorMessages:
    def __init__(self, message="Generic error"):
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.showMessage(message)
        self.error_dialog._exec()