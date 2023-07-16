"""processor_tools.processor - processor class definition"""

from typing import Optional, Any


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["BaseProcessor"]


class BaseProcessor:
    """
    Base class for processor implementations

    :param context: container object storing configuration values that define the processor state
    """

    def __init__(self, context: Optional[Any] = None):
        """
        Constructor method
        """

        self.context = context if context is not None else {}


if __name__ == "__main__":
    pass
