import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent

from mpl_pan_zoom import zoom_factory


def test_zoom_preserves_pan_position():
    """
    Test that zoom_factory preserves the canvas position after panning.

    This tests the issue reported in https://github.com/mpl-extensions/mpl-pan-zoom/issues/7
    where scrolling events would reset the view to the pre-pan position.
    """
    # Create a figure and axis with some data
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)

    # Set initial limits
    initial_xlim = (2, 8)
    initial_ylim = (-1, 1)
    ax.set_xlim(initial_xlim)
    ax.set_ylim(initial_ylim)

    # Enable zoom with auto_centering=False (default)
    disconnect_zoom = zoom_factory(ax, base_scale=1.5, auto_centering=False)

    # Store the initial limits for reference if needed
    # orig_xlim = ax.get_xlim()

    # Simulate panning by directly changing the axis limits
    # (as would happen when using pan mode and dragging)
    panned_xlim = (4, 10)  # Panned to the right
    panned_ylim = (-0.5, 1.5)  # Panned up
    ax.set_xlim(panned_xlim)
    ax.set_ylim(panned_ylim)

    # Force a draw to ensure the new limits are applied
    fig.canvas.draw_idle()

    # Get the center of the panned view for the zoom event
    zoom_x = (panned_xlim[0] + panned_xlim[1]) / 2
    zoom_y = (panned_ylim[0] + panned_ylim[1]) / 2

    # Simulate a scroll event (zoom in) at the center of the panned view
    scroll_event = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,  # pixel coordinates not used
        y=0,  # pixel coordinates not used
        button="up",  # zoom in
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    # Set the data coordinates
    scroll_event.inaxes = ax
    scroll_event.xdata = zoom_x
    scroll_event.ydata = zoom_y

    # Process the scroll event
    fig.canvas.callbacks.process("scroll_event", scroll_event)

    # Get the limits after zooming
    zoomed_xlim = ax.get_xlim()
    zoomed_ylim = ax.get_ylim()

    # The view should be zoomed in but centered around the panned position,
    # NOT reset to the original position
    # Check that the center after zooming is close to the panned center
    zoomed_center_x = (zoomed_xlim[0] + zoomed_xlim[1]) / 2
    assert abs(zoomed_center_x - zoom_x) < 0.1, (
        f"After zoom, x center should be preserved. "
        f"Got center {zoomed_center_x} vs expected {zoom_x}"
    )

    zoomed_center_y = (zoomed_ylim[0] + zoomed_ylim[1]) / 2
    assert abs(zoomed_center_y - zoom_y) < 0.1, (
        f"After zoom, y center should be preserved. "
        f"Got center {zoomed_center_y} vs expected {zoom_y}"
    )

    # The zoom should have made the range smaller (zoomed in)
    zoomed_xrange = zoomed_xlim[1] - zoomed_xlim[0]
    panned_xrange = panned_xlim[1] - panned_xlim[0]
    assert zoomed_xrange < panned_xrange, (
        f"Zoom in should reduce x range. Got {zoomed_xrange} vs {panned_xrange}"
    )

    zoomed_yrange = zoomed_ylim[1] - zoomed_ylim[0]
    panned_yrange = panned_ylim[1] - panned_ylim[0]
    assert zoomed_yrange < panned_yrange, (
        f"Zoom in should reduce y range. Got {zoomed_yrange} vs {panned_yrange}"
    )

    # Clean up
    disconnect_zoom()
    plt.close(fig)


def test_zoom_with_auto_centering():
    """
    Test zoom_factory with auto_centering=True.

    When auto_centering is True, zooming out should return to the original center.
    """
    # Create a figure and axis with some data
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)

    # Set initial limits
    initial_xlim = (2, 8)
    initial_ylim = (-1, 1)
    ax.set_xlim(initial_xlim)
    ax.set_ylim(initial_ylim)

    # Calculate original center
    orig_center_x = (initial_xlim[0] + initial_xlim[1]) / 2
    orig_center_y = (initial_ylim[0] + initial_ylim[1]) / 2

    # Enable zoom with auto_centering=True
    disconnect_zoom = zoom_factory(ax, base_scale=1.5, auto_centering=True)

    # First zoom in at an off-center location
    zoom_x = 3  # Left of center
    zoom_y = 0.5  # Above center

    # Simulate a scroll event (zoom in)
    scroll_in = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,
        y=0,
        button="up",  # zoom in
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    scroll_in.inaxes = ax
    scroll_in.xdata = zoom_x
    scroll_in.ydata = zoom_y

    fig.canvas.callbacks.process("scroll_event", scroll_in)

    ax.get_xlim()  # Just update the view
    ax.get_ylim()

    # Now zoom out
    scroll_out = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,
        y=0,
        button="down",  # zoom out
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    scroll_out.inaxes = ax
    scroll_out.xdata = zoom_x
    scroll_out.ydata = zoom_y

    fig.canvas.callbacks.process("scroll_event", scroll_out)

    zoomed_out_xlim = ax.get_xlim()
    zoomed_out_ylim = ax.get_ylim()

    # With auto_centering=True, when zooming out past the original range,
    # the view should center on the original center
    zoomed_out_center_x = (zoomed_out_xlim[0] + zoomed_out_xlim[1]) / 2
    zoomed_out_center_y = (zoomed_out_ylim[0] + zoomed_out_ylim[1]) / 2

    # The center should be close to the original center when zoomed out
    # (within some tolerance due to the zoom factor)
    assert abs(zoomed_out_center_x - orig_center_x) < 0.5, (
        f"With auto_centering, x center should return close to original. "
        f"Got {zoomed_out_center_x} vs {orig_center_x}"
    )
    assert abs(zoomed_out_center_y - orig_center_y) < 0.1, (
        f"With auto_centering, y center should return close to original. "
        f"Got {zoomed_out_center_y} vs {orig_center_y}"
    )

    # Clean up
    disconnect_zoom()
    plt.close(fig)


def test_zoom_in_and_out():
    """
    Test basic zoom in and out functionality.
    """
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.cos(x)
    ax.plot(x, y)

    initial_xlim = ax.get_xlim()
    initial_ylim = ax.get_ylim()
    initial_xrange = initial_xlim[1] - initial_xlim[0]
    initial_yrange = initial_ylim[1] - initial_ylim[0]

    # Enable zoom
    disconnect_zoom = zoom_factory(ax, base_scale=2.0)

    # Get center point for zoom
    center_x = (initial_xlim[0] + initial_xlim[1]) / 2
    center_y = (initial_ylim[0] + initial_ylim[1]) / 2

    # Zoom in
    scroll_in = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,
        y=0,
        button="up",
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    scroll_in.inaxes = ax
    scroll_in.xdata = center_x
    scroll_in.ydata = center_y

    fig.canvas.callbacks.process("scroll_event", scroll_in)

    zoomed_xlim = ax.get_xlim()
    zoomed_ylim = ax.get_ylim()
    zoomed_xrange = zoomed_xlim[1] - zoomed_xlim[0]
    zoomed_yrange = zoomed_ylim[1] - zoomed_ylim[0]

    # Check that we zoomed in (smaller range)
    assert zoomed_xrange < initial_xrange
    assert zoomed_yrange < initial_yrange
    # Check that we're still centered
    assert abs((zoomed_xlim[0] + zoomed_xlim[1]) / 2 - center_x) < 0.01
    assert abs((zoomed_ylim[0] + zoomed_ylim[1]) / 2 - center_y) < 0.01

    # Zoom out
    scroll_out = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,
        y=0,
        button="down",
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    scroll_out.inaxes = ax
    scroll_out.xdata = center_x
    scroll_out.ydata = center_y

    fig.canvas.callbacks.process("scroll_event", scroll_out)

    final_xlim = ax.get_xlim()
    final_ylim = ax.get_ylim()

    # Should be back to original (within floating point tolerance)
    assert abs(final_xlim[0] - initial_xlim[0]) < 0.01
    assert abs(final_xlim[1] - initial_xlim[1]) < 0.01
    assert abs(final_ylim[0] - initial_ylim[0]) < 0.01
    assert abs(final_ylim[1] - initial_ylim[1]) < 0.01

    # Clean up
    disconnect_zoom()
    plt.close(fig)


def test_zoom_outside_axes():
    """
    Test that zoom events outside the axes are ignored.
    """
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    ax.plot(x, y)

    initial_xlim = ax.get_xlim()
    initial_ylim = ax.get_ylim()

    # Enable zoom
    disconnect_zoom = zoom_factory(ax)

    # Create a scroll event outside the axes
    scroll_event = MouseEvent(
        name="scroll_event",
        canvas=fig.canvas,
        x=0,
        y=0,
        button="up",
        key=None,
        step=1,
        dblclick=False,
        guiEvent=None,
    )
    # Set inaxes to None to simulate event outside axes
    scroll_event.inaxes = None
    scroll_event.xdata = None
    scroll_event.ydata = None

    fig.canvas.callbacks.process("scroll_event", scroll_event)

    # Limits should not have changed
    assert ax.get_xlim() == initial_xlim
    assert ax.get_ylim() == initial_ylim

    # Clean up
    disconnect_zoom()
    plt.close(fig)
