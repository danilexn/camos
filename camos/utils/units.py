# -*- coding: utf-8 -*-
# Created on Tue Jul 06 2021
# Last modified on Tue Jul 06 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import warnings

length = {
    "Meters": "m",
    "Centimeters": "cm",
    "Millimeters": "mm",
    "Microns": "μm",
    "Inches": "in",
}

time = {
    "Seconds": "s",
    "Milliseconds": "ms",
    "Microseconds": "μm",
    "Minutes": "min",
    "Hours": "h",
    "Days": "d",
}

configuration = None


def get_length():
    try:
        current_configuration = configuration.readConfiguration()
        return length[current_configuration["Units/Length"]]
    except:
        warnings.warn("Could not load the length units, loading μm as default")
        return "μm"


def get_time():
    try:
        current_configuration = configuration.readConfiguration()
        return length[current_configuration["Units/Time"]]
    except:
        warnings.warn("Could not load the time units, loading s as default")
        return "s"
