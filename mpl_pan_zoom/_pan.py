__all__ = [
    "PanManager",
]


class PanManager:
    """
    Enable panning a plot with any mouse button.

    .. code-block:: python

       pan = PanManager(my_figure)
       # Let it be disabled and garbage collected
       pan = None

    Parameters
    ----------
    button : int
        Determines which button will be used (default right click).
        Left: 1
        Middle: 2
        Right: 3
    """

    def __init__(self, fig, button):
        self.fig = fig
        self._id_drag = None
        self.button = button
        self._id_press = None
        self._id_release = None

        self.enable()

    @property
    def enabled(self) -> bool:
        """Status of the PanManager, whether it's enabled or disabled."""
        return self._id_press is not None and self._id_release is not None

    def enable(self):
        """
        Enable the PanManager.

        It should not be necessary to call this function
        unless it's used after a call to :meth:`PanManager.disable`.

        Raises
        ------
        RuntimeError
            If the PanManager is already enabled.
        """
        if self.enabled:
            raise RuntimeError("The PanManager is already enabled")

        self._id_press = self.fig.canvas.mpl_connect("button_press_event", self.press)
        self._id_release = self.fig.canvas.mpl_connect(
            "button_release_event", self.release
        )

    def disable(self):
        """
        Disable the PanManager.

        Raises
        ------
        RuntimeError
            If the PanManager is already disabled.
        """
        if not self.enabled:
            raise RuntimeError("The PanManager is already disabled")

        self.fig.canvas.mpl_disconnect(self._id_press)
        self.fig.canvas.mpl_disconnect(self._id_release)

        self._id_press = None
        self._id_release = None
        # just to be sure
        if self.fig.canvas.widgetlock.isowner(self):
            self.fig.canvas.widgetlock.release(self)

    def _cancel_action(self):
        self._xypress = []
        if self._id_drag:
            self.fig.canvas.mpl_disconnect(self._id_drag)
            self._id_drag = None
        if self.fig.canvas.widgetlock.isowner(self):
            self.fig.canvas.widgetlock.release(self)

    def press(self, event):
        if event.button != self.button:
            self._cancel_action()
            return
        if not self.fig.canvas.widgetlock.available(self):
            return

        self.fig.canvas.widgetlock(self)

        x, y = event.x, event.y

        self._xypress = []
        for i, a in enumerate(self.fig.get_axes()):
            if (
                x is not None
                and y is not None
                and a.in_axes(event)
                and a.get_navigate()
                and a.can_pan()
            ):
                a.start_pan(x, y, event.button)
                self._xypress.append((a, i))
                self._id_drag = self.fig.canvas.mpl_connect(
                    "motion_notify_event", self._mouse_move
                )

    def release(self, event):
        self._cancel_action()
        self.fig.canvas.mpl_disconnect(self._id_drag)

        for a, _ind in self._xypress:
            a.end_pan()
        if not self._xypress:
            self._cancel_action()
            return
        self._cancel_action()

    def _mouse_move(self, event):
        for a, _ind in self._xypress:
            # safer to use the recorded button at the _press than current
            # button: # multiple button can get pressed during motion...
            a.drag_pan(1, event.key, event.x, event.y)
        self.fig.canvas.draw_idle()
