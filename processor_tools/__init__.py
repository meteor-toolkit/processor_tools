"""processor_tools - Tools to support the developing of processing pipelines"""

from importlib.metadata import version as _pkg_version, PackageNotFoundError

try:
    __version__ = _pkg_version("processor_tools")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__author__ = "MetEOR Toolkit Team <team@comet-toolkit.org>"
__all__ = [
    "BaseProcessor",
    "ProcessorFactory",
    "NullProcessor",
    "read_config",
    "write_config",
    "build_configdir",
    "Context",
    "set_global_supercontext",
    "clear_global_supercontext",
    "find_config",
]

from typing import List, Tuple, Union

GLOBAL_SUPERCONTEXT: List[Tuple["Context", Union[None, str]]] = []

from processor_tools.processor import BaseProcessor, ProcessorFactory, NullProcessor
from processor_tools.config.config_io import (
    read_config,
    write_config,
    build_configdir,
    find_config,
)
from processor_tools.context import (
    Context,
    set_global_supercontext,
    clear_global_supercontext,
)
