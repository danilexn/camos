# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph.console
import camos

app = pg.mkQApp()

namespace = {"np": np, "camos": camos}
version = "v0.1"

text = """# CaMOS {}.
# Interactive Python Console;
# Loaded modules:
# - numpy (as np)
# - camos
""".format(
    version
)


def open_console():
    c = pyqtgraph.console.ConsoleWidget(namespace=namespace, text=text)
    c.show()
    c.setWindowTitle("CaMOS - Console")
