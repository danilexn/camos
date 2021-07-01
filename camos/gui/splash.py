import time

from PyQt5 import QtCore, QtGui, QtWidgets


__docformat__ = "restructuredtext"


class SplashScreen(QtWidgets.QSplashScreen):
    """
    The application splash screen.
    :Parameter png: the pixmap image displayed as a splash screen.
    """

    def __init__(self, png):
        """
        Initialize the application.
        Create a splash screen and ties it to a painter which will
        be in charge of displaying the needed messages.
        """

        super(SplashScreen, self).__init__(png)
        self.msg = ""

    def drawContents(self, painter):
        """Draw the contents of the splash screen using the given painter.
        This is an overloaded method. It draws contents with the origin
        translated by a certain offset.
        :Parameter painter: the painter used to draw the splash screen
        """

        painter.setPen(QtGui.QColor(QtCore.Qt.white))
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 200, self.msg)

    def drawMessage(self, msg):
        """
        Draw the message text onto the splash screen.
        :Parameter msg: the message to be displayed
        """

        QtWidgets.qApp.processEvents()
        self.msg = msg
        self.showMessage(self.msg)
        time.sleep(0.500)
        self.clearMessage()
