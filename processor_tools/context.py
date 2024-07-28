"""processor.context - customer container from processing state"""

import os.path
from typing import Optional, Dict, Any, List, Union, Tuple
from copy import deepcopy
import collections.abc
from processor_tools import GLOBAL_SUPERCONTEXT
from processor_tools import read_config, find_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["Context", "set_global_supercontext"]


class Context:
    """
    Class to determine and store processing state

    :param config: processing configuration data, either:

    * dictionary of configuration data
    * path of configuration file or directory containing set of configuration files
    * list of paths (earlier in the list overwrites later in the list)

    :param supercontext: context supercontext or list of supercontexts, configuration values of which override those defined in the context. Each defined as context object or tuple of:

    * `supercontext` (*Context*) - supercontext object
    * `section` (*str*) -  name of section of supercontext to apply as supercontext

    For example:

    .. code-block:: python

       supercontext = Context({"section": {"val1": 1 , "val2", 2}})
       (supercontext, "section")
    """

    # default_config class variable enables you to set configuration file(s)/directory(ies) of files that are
    # loaded every time the class is initialised. Configuration values from these files come lower in the priority
    # list than those defined at init.
    default_config: Optional[Union[str, List[str]]] = None

    def __init__(
        self,
        config: Optional[Union[str, List[str], dict]] = None,
        supercontext: Optional[Union["Context", Tuple["Context", str]]] = None
    ) -> None:

        # initialise attributes
        self._config_values: Dict[str, Any] = {}
        self._supercontext: List[Tuple["Context", Union[None, str]]] = []

        if supercontext is not None:
            self.supercontext = supercontext

        # init default config path
        default_config_paths: List[str] = []
        if isinstance(self.default_config, str):
            default_config_paths = [self.default_config]
        elif isinstance(self.default_config, list):
            default_config_paths = self.default_config

        # init user config paths
        if isinstance(config, str):
            config_paths = [config] + default_config_paths
        elif isinstance(config, list):
            config_paths = config + default_config_paths
        else:
            config_paths = default_config_paths

        # open config paths
        for config_path in reversed(config_paths):
            if os.path.isdir(config_path):
                for p in find_config(config_path):
                    self.update_config_from_file(p)

            else:
                self.update_config_from_file(config_path)

        if isinstance(config, dict):
            self._config_values.update(config)

    @property
    def supercontext(self) -> List[Tuple["Context", Union[None, str]]]:
        """
        Return context supercontexts

        :return: supercontexts
        """

        return self._supercontext

    @supercontext.setter
    def supercontext(self, supercontext: Union[Tuple["Context", str], "Context"]):
        """
        Sets context supercontext, configuration values of which override those defined in the context

        :param supercontext: supercontext or list of supercontexts - defined as context object or tuple of:

        * `supercontext` (*Context*) - supercontext object
        * `section` (*str*) -  name of section of supercontext to apply as supercontext

        For example:

        .. code-block:: python

           supercontext = Context({"section": {"val1": 1 , "val2", 2}})
           (supercontext, "section")

        """

        if isinstance(supercontext, tuple) or isinstance(supercontext, self.__class__):
            supercontext = [supercontext]

        if not isinstance(supercontext, list):
            raise TypeError("'supercontext' must be defined as one of type [`processor_tools.Context`, `tuple`, `list`]")

        for i, supercontext_i in enumerate(supercontext):
            if isinstance(supercontext_i, self.__class__):
                supercontext[i] = (supercontext_i, None)

            elif isinstance(supercontext_i, tuple):
                if not (isinstance(supercontext_i[0], self.__class__) and (isinstance(supercontext_i[1], str) or (supercontext_i[1] is None))):
                    raise TypeError("supercontext tuple must be of type `(processor_tools.Context, str | None)`")

            else:
                raise TypeError("supercontext definition must be either `processor_tools.Context` or  `(processor_tools.Context, str | None)`")

        self._supercontext = supercontext

    @supercontext.deleter
    def supercontext(self):
        """
        Deletes context supercontexts
        """

        self._supercontext = []

    @property
    def is_global_supercontext(self) -> bool:
        """
        Returns `True` if context object has been set as a global supercontext, else `False`

        :return: global supercontext flag
        """
        if self in GLOBAL_SUPERCONTEXT:
            return True
        else:
            return False

    def update_config_from_file(self, path: str) -> None:
        """
        Update config values from file

        :param path: config file path
        """

        config = read_config(path)
        self._config_values.update(config)

    @property
    def config_values(self) -> Any:
        """
        Returns defined configuration values

        :return: configuration values
        """

        return self._config_values

    def set(self, name: str, value: Any):
        """
        Sets config data

        :param name: config data name
        :param value: config data value
        """

        self._config_values[name] = value

    def __setitem__(self, name: str, value: Any):
        """
        Sets config data

        :param name: config data name
        :param value: config data value
        """
        self.set(name, value)

    def get(self, name: str, default: Any = None) -> Any:
        """
        Get config value if defined, else return default

        :param name: config data name
        :param default: default value to return if name not defined in config
        :return: config value if defined, else return default
        """

        return self.config_values[name] if name in self.get_config_names() else default

    def __getitem__(self, name: str) -> Any:
        """
        Get config value

        :param name: config data name
        :return: config value
        """

        return self.get(name)

    def get_config_names(self) -> List[str]:
        """
        Get available config value names

        :return: config value names
        """

        return list(self.config_values.keys())

    def keys(self) -> List[str]:
        """
        Get available config value names

        :return: config value names
        """

        return self.get_config_names()


class set_global_supercontext:
    """
    Sets a context object to become a global supercontext for other context objects

    :param context: Processor state definition object

    Can be run with a `with` statement, as follows

    .. code-block: python

       from processor_tools import Context, set_global_supercontext

       my_context = Context()

       with set_global_supercontext:
           run_process()

    In this example, `my_context` is set as the global supercontext within the scope of the `with` statement and then removed after.
    """

    def __init__(self, context: Context):
        self(context)

    def __call__(self, context: Context):

        if isinstance(context, Context) or isinstance(context, tuple):
            GLOBAL_SUPERCONTEXT.append(context)

        else:
            raise TypeError("Argument 'context' must be of type 'processor_tools.Context'")

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        del GLOBAL_SUPERCONTEXT[-1]


if __name__ == "__main__":
    pass
