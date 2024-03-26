"""processor_tools - Tools to support the developing of processing pipelines"""

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["BaseProcessor", "ProcessorFactory", "NullProcessor"]

from ._version import get_versions
from processor_tools.processor import BaseProcessor, ProcessorFactory, NullProcessor

__version__ = get_versions()["version"]
del get_versions
