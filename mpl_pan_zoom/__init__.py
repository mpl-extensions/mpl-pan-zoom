try:
    from importlib.metadata import version

    __version__ = version("mpl-pan-zoom")
except ImportError:
    # For Python < 3.8 or if package not installed
    try:
        from ._version import version as __version__
    except ImportError:
        __version__ = "unknown"
__author__ = "Ian Hunt-Isaak"
__email__ = "ianhuntisaak@gmail.com"

from matplotlib.backend_bases import MouseButton

from ._pan import PanManager
from ._zoom import zoom_factory

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "PanManager",
    "zoom_factory",
    "MouseButton",
]
