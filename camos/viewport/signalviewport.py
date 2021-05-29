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
            :event: the trigger event
            """
            print("Double clicked hehe!")
            print(event.pos)
            print(event.button)
            pass

    def add_last_track(self, title="Calcium signal"):
        data = self.model.data[-1]
        g_obj_grid = GridSignalsObj("2d", data, plt_as="col")
        self.scene.add_to_subplot(g_obj_grid, title=title)