"""processor_tools - Tools to support the developing of processing pipelines"""

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["BaseProcessor", "ProcessorFactory", "NullProcessor", "read_config", "write_config", "Context", "CustomCmdClassUtils"]

from ._version import get_versions
from processor_tools.processor import BaseProcessor, ProcessorFactory, NullProcessor
from processor_tools.config_io import read_config, write_config
from processor_tools.context import Context
from processor_tools.setup_utils import CustomCmdClassUtils

__version__ = get_versions()["version"]
del get_versions
