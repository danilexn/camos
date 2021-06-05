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
import collections
import functools

from PyQt5 import QtCore, QtGui, QtWidgets


def getCamosApp():
    """Get a reference to the `camosApp` instance.
    This is useful namely for plugins.
    """

    camosApp = None
    widgets = QtWidgets.QApplication.instance().allWidgets()
    for widget in widgets:
        if str(widget.objectName()) == "camosGUI":
            camosApp = widget.camosApp
            break

    return camosApp


def getApp():
    return getCamosApp()


def getGui():
    """Small wrapper to hide the fact that camosApp object contains gui.
    :return: main window object
    """
    return getApp().gui


def getModels():
    """Small wrapper to hide that camosApp.gui object contains dbs_tree_model.
    :return: the DBs tree model
    """
    return getGui().model, getGui().signalmodel


def getViews():
    """Small wrapper to hide that camosApp.gui object contains dbs_tree_view.
    :return: the DBs tree view
    """
    return getGui().viewport, getGui().signalviewport


def long_action(message=None):
    """Decorator that changes the cursor to the wait cursor.
    Used with functions that take some time finish. The provided
    message is displayed in the status bar while the function is
    running (the status bar is cleaned afterwards). If the message is
    not provided then the status bar is not updated.
    :parameter message: string to display in status bar
    """

    def _long_action(f):
        @functools.wraps(f)
        def __long_action(*args, **kwargs):
            status_bar = getGui().statusBar()
            if message is not None:
                status_bar.showMessage(message)
            QtWidgets.QApplication.setOverrideCursor(
                QtGui.QCursor(QtCore.Qt.WaitCursor)
            )
            try:
                res = f(*args, **kwargs)
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
                if message is not None:
                    status_bar.clearMessage()
            return res

        return __long_action

    return _long_action


def insertInMenu(menu, entries, uid):
    """Insert entries to the given menu before the action named uid.
    The function accept a QAction/QMenu or an iterable. The entries will
    be added before the action whose name is uid.
    :Parameters:
    - `menu`: the menu or context menu being updated
    - `entries`: QAction/Qmenu object or a list of such objects
    - `uid`: indicates the insertion position for the new entries
    :return: None
    """

    if not isinstance(entries, collections.Iterable):
        entries = [entries]

    if isinstance(entries[0], QtWidgets.QAction):
        menu.insertEntry = menu.insertAction
    elif isinstance(entries[0], QtWidgets.QMenu):
        menu.insertEntry = menu.insertMenu

    for item in menu.actions():
        if item.objectName() == uid:
            for a in entries:
                qa = menu.insertEntry(item, a)


def addToMenu(menu, entries):
    """Add entries at the end of the given menu.
    The function accept a QAction/QMenu or an iterable. Entries will be
    preceded with a separator and added at the end of the menu.
    :Parameters:
    - `menu`: the menu or context menu being updated
    - `entries`: QAction/QMenu object or a list of such objects
    :return: None
    """

    if not isinstance(entries, collections.Iterable):
        entries = [entries]

    if isinstance(entries[0], QtWidgets.QAction):
        menu.addEntry = menu.addAction
    elif isinstance(entries[0], QtWidgets.QMenu):
        menu.addEntry = menu.addMenu

    menu.addSeparator()
    for a in entries:
        menu.addEntry(a)


def addActions(target, actions, actions_dict):
    """Add a list of QActions to a menu or a toolbar.
    This is a helper function which make easier to add QActions to a
    menu or a toolbar. Separators and submenus are also handled by this
    method.
    :Parameters:
    - `target`: the menu or toolbar where actions will be added
    - `actions`: a sequence of keywords/None/QMenu used to get actions
                 from a mapping
    - `actions_dict`: a mapping of actions
    """

    for action in actions:
        if action is None:
            target.addSeparator()
        elif isinstance(action, QtWidgets.QMenu):
            target.addMenu(action)
        else:
            target.addAction(actions_dict[action])
