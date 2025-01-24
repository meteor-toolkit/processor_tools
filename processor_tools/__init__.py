"""processor_tools - Tools to support the developing of processing pipelines"""

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
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
    "CustomCmdClassUtils",
    "find_config",
]

from typing import List, Tuple, Union

GLOBAL_SUPERCONTEXT: List[Tuple["Context", Union[None, str]]] = []

from ._version import get_versions
from processor_tools.processor import BaseProcessor, ProcessorFactory, NullProcessor
from processor_tools.config_io import (
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
from processor_tools.setup_utils import CustomCmdClassUtils

__version__ = get_versions()["version"]
del get_versions
