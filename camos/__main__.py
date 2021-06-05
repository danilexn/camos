# coding=utf-8
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
import signal
import sys
import locale
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from darktheme.widget_template import DarkPalette

from camos.app import camosApp
import camos.utils.settings as settings
import camos.utils.apptools

_I18N_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")


def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    exit(0)


def _set_credentials(app):
    """Specify the organization's Internet domain.
    When the Internet domain is set, it is used on Mac OS X instead of
    the organization name, since Mac OS X applications conventionally
    use Internet domains to identify themselves
    """
    app.setOrganizationDomain("camos.org")
    app.setOrganizationName("camos")
    app.setApplicationName("camos")
    app.setApplicationVersion(settings.getVersion())


def _set_locale(app):
    """Set locale and load translation if available.
    Localize the application using the system locale numpy seems to
    have problems with decimal separator in some locales (catalan,
    german...) so C locale is always used for numbers.
    """
    locale.setlocale(locale.LC_ALL, "")
    locale.setlocale(locale.LC_NUMERIC, "C")

    locale_name = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    if translator.load("camos_" + locale_name, _I18N_PATH):
        app.installTranslator(translator)
    return translator


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    app = QtWidgets.QApplication(sys.argv)
    _set_credentials(app)
    # translator = _set_locale(app)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    _app = camosApp()
    camosApp_second = camos.utils.apptools.getApp()
    sys.exit(app.exec_())
