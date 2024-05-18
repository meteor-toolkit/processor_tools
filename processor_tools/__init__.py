"""processor_tools - Tools to support the developing of processing pipelines"""

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = [
    "BaseProcessor",
    "ProcessorFactory",
    "NullProcessor",
    "read_config",
    "DatabaseCRUD",
]

from ._version import get_versions
from processor_tools.processor import BaseProcessor, ProcessorFactory, NullProcessor
from processor_tools.config_io import read_config
from processor_tools.db_crud import DatabaseCRUD

__version__ = get_versions()["version"]
del get_versions
