# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.opening import Opening
import camos.utils.apptools as apptools

import pickle


class OpenImage(Opening):
    analysis_name = "Open View"

    def __init__(self, *args, **kwargs):
        super(OpenImage, self).__init__(extensions="cms File (*.cms)", *args, **kwargs)

    def _run(self):
        # Added so we can load CMOS chip image
        dp = pickle.load(open(self.filename, "rb"))
        apptools.getApp().gui.setup_model(dp)
