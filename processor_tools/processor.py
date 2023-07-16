"""processor_tools.processor - processor class definition"""

from typing import Optional, Type, Dict, Union, List, Any
import inspect
import sys
import importlib


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["BaseProcessor", "ProcessorFactory"]


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


class ProcessorFactory:
    """
    Container for sets of processor objects

    :param module_name: Name (or list of names) of submodule(s) to find processor classes to populate factory with (e.g. ``package.processors``)
    :param required_baseclass: filter for classes that only subclass this class
    """

    def __init__(
            self,
            module_name: Optional[Union[str, List[str]]] = None,
            required_baseclass: Optional[Type] = BaseProcessor
    ) -> None:

        self._processors: Dict[str, Type] = {}
        self._module_name: Union[None, str, List[str]] = module_name
        self._required_baseclass: Type = required_baseclass

        # find processor classes
        if self._module_name is not None:
            self._processors = self._find_processors(self._module_name)

    def _find_processors(
        self, module_name: Union[str, List[str]]
    ) -> Dict[str, Type]:
        """
        Returns dictionary of ````processor_tools.processor.BaseProcessor```` subclasses contained within a defined module (or set of modules)

        :param module_name: Name (or list of names) of submodule(s) to find processor classes in (e.g. ``package.processors``)

        :return: processor classes
        """

        if type(module_name) == str:
            module_name = [module_name]

        processors = {}

        # find processors per module
        for mod_name in module_name:
            importlib.import_module(mod_name)
            mod_classes = {
                cls[0]: cls[1]
                for cls in inspect.getmembers(sys.modules[mod_name], inspect.isclass)
            }

            # omit factory classes and classes not of required baseclass (if set)
            omit_classes = []
            for cls_name, cls in mod_classes.items():

                if self._required_baseclass is not None:
                    if not issubclass(cls, self._required_baseclass):
                        omit_classes.append(cls_name)

            for o_cls in omit_classes:
                del mod_classes[o_cls]

            # Remove baseclass if in dictionary
            if self._required_baseclass.__name__ in mod_classes:
                del mod_classes[self._required_baseclass.__name__]

            # store in dict
            processors.update(mod_classes)

        return processors

    def keys(self) -> List[str]:
        """
        Returns list of the names of processor classes contained within the object

        :return: List of processor classes
        """
        return list(self._processors.keys())

    def __getitem__(self, name: str) -> Union[None, Type]:
        """
        Returns named processor contained within the object

        :param name: processor class name (case insensitive)
        :return: processor class (returns None if class name not found in container)
        """

        # find class name in case insensitive way
        cls_names = self.keys()
        lower_cls_names = [c.lower() for c in cls_names]

        if name.lower() not in lower_cls_names:
            return None
        else:
            cls_name = cls_names[lower_cls_names.index(name.lower())]
            return self._processors[cls_name]

    def __setitem__(self, name: str, cls: Type) -> None:
        """
        Adds item to container

        :param name: processor class name
        :param cls: processor class object, must be subclass of ``processor_tools.processor.BaseProcessor``
        """

        # check if class of required baseclass (if set)
        if self._required_baseclass is not None:
            if not issubclass(cls, self._required_baseclass):
                raise ValueError(
                    str(cls) + "must be subclass of " + str(self._required_baseclass)
                )

        self._processors[name] = cls

    def __delitem__(self, name: str) -> None:
        """
        Deletes item from container

        :param name: processor class name
        """

        # use functionality from dict
        del self._processors[name]


if __name__ == "__main__":
    pass
