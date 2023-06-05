from pkg_resources import DistributionNotFound, get_distribution
from importlib.metadata import PackageNotFoundError
try:
    __version__ = get_distribution(__name__).version
except (DistributionNotFound, PackageNotFoundError):
    __version__ = "unknown"

from .app import *
