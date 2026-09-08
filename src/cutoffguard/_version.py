"""Package version lookup kept separate to avoid public-API import cycles."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("cutoffguard")
except PackageNotFoundError:
    __version__ = "0.2.0"
