# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from visbrain.objects import GridSignalsObj, SceneObj


class SignalViewPort:
    def __init__(self, model=None, parent=None):
        self.scene = SceneObj(bgcolor="black")
        canvas = self.scene.canvas
        self.model = model
        self.parent = parent

        @canvas.events.mouse_double_click.connect
        def on_mouse_double_click(event):
            """Executed function when double click mouse over Brain canvas.
            Args:
                event: the trigger event
            """
            print(event.pos)
            print(event.source.position)
            print(event.button)
            pass

    def add_last_track(self, **kwargs):
        self.add_track(-1, **kwargs)

    def add_track(self, layer = 0, title="Calcium signal"):
        data = self.model.data[layer]
        name = self.model.names[layer]
        g_obj_grid = GridSignalsObj("2d", data, plt_as="col")
        self.scene.add_to_subplot(g_obj_grid, title=name)
