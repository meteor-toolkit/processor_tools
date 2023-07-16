"""processor_tools.processor_builder - tools for building configurable processors"""

from typing import Optional, Type, Dict, Union, List
import inspect
import sys
import abc
import importlib
from processor_tools.processor import BaseProcessor

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["ProcessorBuilder", "BaseProcessorFactory"]


class ProcessorBuilder:
    """
    Class that assembles processor from set of configurable sub-processors
    """

    pass


class BaseProcessorFactory:
    """
    Base class for containers of set of processor objects
    """

    @property
    def _module_name(self) -> Union[None, str, List[str]]:
        """Name (or list of names) of submodule(s) to find processor classes in (e.g. ``package.processors``)"""
        return None

    def __init__(self) -> None:

        # find processor classes
        self._processors: Dict[str, Type[BaseProcessor]] = (
            self._find_processors(self._module_name)
            if self._module_name is not None
            else {}
        )

    def _find_processors(
        self, module_name: Union[str, List[str]]
    ) -> Dict[str, Type[BaseProcessor]]:
        """
        Returns dictionary of ````processor_tools.processor.BaseProcessor```` subclasses contained within a defined module (or set of modules)

        :param module_name: Name (or list of names) of submodule(s) to find processor classes in (e.g. ``package.processors``)

        :return: processor classes
        """

        required_baseclass = BaseProcessor

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
                if issubclass(cls, self.__class__.__base__) or (
                    cls == self.__class__.__base__
                ):
                    omit_classes.append(cls_name)

                if required_baseclass is not None:
                    if not issubclass(cls, required_baseclass):
                        omit_classes.append(cls_name)

            for o_cls in omit_classes:
                del mod_classes[o_cls]

            # Remove baseclass if in dictionary
            if required_baseclass.__name__ in mod_classes:
                del mod_classes[required_baseclass.__name__]

            # store in dict
            processors.update(mod_classes)

        return processors

    def keys(self) -> List[str]:
        """
        Returns list of the names of processor classes contained within the object

        :return: List of processor classes
        """
        return list(self._processors.keys())

    def __getitem__(self, name: str) -> Union[None, Type[BaseProcessor]]:
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

    def __setitem__(self, name: str, cls: Type[BaseProcessor]) -> None:
        """
        Adds item to container

        :param name: processor class name
        :param cls: processor class object, must be subclass of ``processor_tools.processor.BaseProcessor``
        """

        required_baseclass = BaseProcessor

        # check if class of required baseclass (if set)
        if required_baseclass is not None:
            if not issubclass(cls, required_baseclass):
                raise ValueError(
                    str(cls) + "must be subclass of " + str(required_baseclass)
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
