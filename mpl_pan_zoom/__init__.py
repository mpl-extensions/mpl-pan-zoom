try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"
__author__ = "Ian Hunt-Isaak"
__email__ = "ianhuntisaak@gmail.com"

from ._zoom import zoom_factory
from ._pan import PanManager
from matplotlib.backend_bases import MouseButton

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "PanManager",
    "zoom_factory",
    "MouseButton",
]
