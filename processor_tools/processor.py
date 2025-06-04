"""processor_tools.processor - processor class definition"""

from typing import Optional, Type, Dict, Union, List, Any
import inspect
import sys
import importlib
from copy import deepcopy


__author__ = ["Sam Hunt <sam.hunt@npl.co.uk>", "Maddie Stedman"]
__all__ = ["BaseProcessor", "ProcessorFactory", "NullProcessor"]


class BaseProcessor:
    """
    Base class for processor implementations

    :param context: container object storing configuration values that define the processor state
    :param processor_path: location of processor name in subprocessor tree
    """

    cls_subprocessors: Union[
        None,
        Dict[str, Union["BaseProcessor", Type["BaseProcessor"], "ProcessorFactory"]],
    ] = None
    """Default set of subprocessors for processor objects of this class"""

    cls_processor_name: Union[None, str] = None
    """Name for processor objects of this class (accessed via ``processor_name`` property - will default to the name of the class is if this class attribute is unset.)"""

    def __init__(
        self,
        context: Optional[Any] = None,
        processor_path: Optional[str] = None,
        **kwargs
    ):
        """
        Constructor method
        """

        # define attributes
        self.context: Any = context if context is not None else {}
        self.processor_path: Optional[str] = processor_path
        self.subprocessors: Dict[str, "BaseProcessor"] = {}

        # if cls_subprocessor set append defined subprocessors to self.subprocessors
        if self.cls_subprocessors is not None:
            for sp_name, sp_obj in self.cls_subprocessors.items():
                self.append_subprocessor(sp_name, sp_obj)

        super().__init__(**kwargs)

    def __str__(self):
        """Custom __str__"""
        return "<Processor: {}>".format(
            self.processor_name,
        )

    def __repr__(self):
        """Custom  __repr__"""
        return str(self)

    @property
    def processor_name(self) -> str:
        """Returns processor name"""

        # return class attribute for processor name if set
        if self.cls_processor_name is not None:
            return self.cls_processor_name

        # default to the name of the class is if this class attribute is unset
        return self.__class__.__name__

    def append_subprocessor(
        self,
        sp_name: str,
        sp_obj: Union["BaseProcessor", Type["BaseProcessor"], "ProcessorFactory"],
    ) -> None:
        """
        Appends instantiation of processor to ``subprocessors`` attribute.

        If subprocessor object is provided as:

        * object - processor object (with updated ``processor_path`` attribute) added to ``subprocessors``.
        * class - class is instantiated, with resultant object added ``subprocessors``
        * factory - class selected from factory - using value from ``self.context`` for target ``processor_path`` - and instantiated, with resultant object added ``subprocessors``

        :param sp_name: name of subprocessor
        :param sp_obj: subprocessor object
        """

        # determine location of processor in subprocessor tree
        if self.processor_path is None:
            sp_path = sp_name
        else:
            sp_path = ".".join([self.processor_path, sp_name])

        # handle subprocessor depending on how it is defined:
        # * factory - class selected from factory and instantiated, with resultant object added subprocessors
        if isinstance(sp_obj, ProcessorFactory):
            try:
                self.subprocessors[sp_name] = sp_obj[self.context['processor'][sp_path]](
                    context=self.context, processor_path=sp_path
                )
            except:
                self.subprocessors[sp_name] = sp_obj[self.context[sp_path]](
                    context=self.context, processor_path=sp_path
                )
        # * if object - processor object add to subprocessors
        elif isinstance(sp_obj, BaseProcessor):
            sp_obj._prepend_processor_path(sp_path)
            self.subprocessors[sp_name] = sp_obj

        # * if class - class is instantiated, with resultant object added ``subprocessors``
        elif issubclass(sp_obj, BaseProcessor):
            self.subprocessors[sp_name] = sp_obj(
                context=self.context, processor_path=sp_path
            )

        else:
            raise TypeError(
                "subprocessor object must be of type: ['BaseProcessor', Type['BaseProcessor'], 'ProcessorFactory']"
            )

    def _prepend_processor_path(self, path: str):
        self.processor_path = path
        self._prepend_subprocessor_path(path, self)

    def _prepend_subprocessor_path(self, path: str, obj):
        for sp_name, sp_cls in obj.subprocessors.items():
            sp_cls.processor_path = ".".join([path, sp_cls.processor_path])
            self._prepend_subprocessor_path(path, sp_cls)

    def run(self, *args: Any) -> Any:
        """
        Runs processor subprocessors sequentially in order, output of each feeding into the next

        :param args: processor input arguments
        :return: output values of final processor
        """

        # if defined run subprocessors in order

        if self.subprocessors is not None:
            # output of previous subprocessor feeds into next, initialise with input value
            proc_args_i = deepcopy(args)

            for sp_name, sp in self.subprocessors.items():
                # handle splat operator correctly for different arg types
                if isinstance(proc_args_i, tuple):
                    if len(proc_args_i) == 1:
                        proc_args_i = sp.run(proc_args_i[0])

                    else:
                        proc_args_i = sp.run(*proc_args_i)

                else:
                    proc_args_i = sp.run(proc_args_i)

            return proc_args_i


class ProcessorFactory:
    """
    Container for sets of processor objects

    :param processors: list of processors to add to factory
    :param module_name: Name (or list of names) of submodule(s) to find processor classes to populate factory with (e.g. ``package.processors``)
    :param required_baseclass: filter for classes that only subclass this class
    """

    def __init__(
        self,
        processors: Optional[List[Type[BaseProcessor]]] = None,
        module_name: Optional[Union[str, List[str]]] = None,
        required_baseclass: Optional[Type] = None,
    ) -> None:
        self._processors: Dict[str, Type] = {}
        self._module_name: Union[None, str, List[str]] = module_name
        self._required_baseclass: Type = (
            required_baseclass if required_baseclass is not None else BaseProcessor
        )

        # add processors
        if processors is not None:
            for processor in processors:
                self.add_processor(processor)

        # find processor classes in module
        if self._module_name is not None:
            self._processors = self._find_processors(self._module_name)

    def _find_processors(self, module_name: Union[str, List[str]]) -> Dict[str, Type]:
        """
        Returns dictionary of ````processor_tools.processor.BaseProcessor```` subclasses contained within a defined module (or set of modules)

        :param module_name: Name (or list of names) of submodule(s) to find processor classes in (e.g. ``package.processors``)

        :return: processor classes
        """

        if isinstance(module_name, str):
            module_name = [module_name]

        module_name.append("processor_tools.processor")
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

    def __getitem__(self, name: str) -> Type:
        """
        Returns named processor contained within the object

        :param name: processor class name (case insensitive)
        :return: processor class (returns None if class name not found in container)
        """

        # find class name in case insensitive way
        cls_names = self.keys()
        lower_cls_names = [c.lower() for c in cls_names]

        if name.lower() not in lower_cls_names:
            raise KeyError(name)
        else:
            cls_name = cls_names[lower_cls_names.index(name.lower())]
            return self._processors[cls_name]

    def add_processor(self, cls: Type[BaseProcessor]) -> None:
        """
        Adds item to container

        :param cls: processor class object, must be subclass of ``processor_tools.processor.BaseProcessor``
        """

        # check if class of required baseclass (if set)
        if self._required_baseclass is not None:
            if not issubclass(cls, self._required_baseclass):
                raise ValueError(
                    str(cls) + "must be subclass of " + str(self._required_baseclass)
                )

        cls_name = (
            cls.cls_processor_name
            if cls.cls_processor_name is not None
            else cls.__name__
        )

        self._processors[cls_name] = cls

    def __delitem__(self, name: str) -> None:
        """
        Deletes item from container

        :param name: processor class name
        """

        # use functionality from dict
        del self._processors[name]


class NullProcessor(BaseProcessor):
    """
    Null processor for processing variables where no processing is required.
    """

    cls_processor_name = "null_processor"

    def run(
        self,
        *args,
        **kwargs,
    ) -> Any:
        return args


if __name__ == "__main__":
    pass
