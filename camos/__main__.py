# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import signal
import sys
import locale
import os
import traceback

from PyQt5 import QtWidgets, QtCore
from darktheme.widget_template import DarkPalette

from camos.app import camosApp
import camos.utils.settings as settings
import camos.utils.apptools
from camos.gui.notification import CaMOSQtNotification
from camos.gui.styles import notification_style
from camos.utils.notifications import Notification

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


def excepthook(exc_type, exc_value, exc_tb):
    tb = "\n".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # ErrorMessages(tb)
    error = Notification("\n; ".join([str(exc_value), tb]), "ERROR")
    CaMOSQtNotification.from_notification(error)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    sys.excepthook = excepthook
    app = QtWidgets.QApplication(sys.argv)
    _set_credentials(app)
    # translator = _set_locale(app)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    # setup stylesheet for the notifications
    app.setStyleSheet(notification_style)
    _app = camosApp()
    camosApp_second = camos.utils.apptools.getApp()
    sys.exit(app.exec_())
