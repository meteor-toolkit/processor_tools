"""processor.context - customer container from processing state"""

import os.path
from typing import Optional, Dict, Any, List, Union, Type, Tuple
from processor_tools import GLOBAL_SUPERCONTEXT
from processor_tools import read_config, find_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["Context"]


class Context:
    """
    Class to determine and store processing state

    :param config: processing configuration data, either:

    * dictionary of configuration data
    * path of configuration file or directory containing set of configuration files
    * list of paths (earlier in the list overwrites later in the list)

    :param supercontext: context supercontext, configuration values of which override those defined in the context. Defined as context object or tuple of:

    * `supercontext` (*Context*) - supercontext object
    * `subsection` (*str*) -  name of subsection of supercontext to apply as supercontext

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
        self._supercontext: Optional[Union["Context", Tuple["Context", str]]] = None

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
        Return context supercontext - including any global supercontext

        :return: supercontext
        """

        if self._supercontext is None:
            return GLOBAL_SUPERCONTEXT

        else:
            instance_supercontext = self._supercontext
            if not isinstance(self._supercontext, list):
                instance_supercontext = [self._supercontext]
            return GLOBAL_SUPERCONTEXT + instance_supercontext

    @supercontext.setter
    def supercontext(self, supercontext: Union[Tuple["Context", str], "Context"]):
        """
        Sets context supercontext, configuration values of which override those defined in the context

        :param supercontext: context object or tuple of:

        * `supercontext` (*Context*) - supercontext object
        * `subsection` (*str*) -  name of subsection of supercontext to apply as supercontext

        For example:

        .. code-block:: python

           supercontext = Context({"section": {"val1": 1 , "val2", 2}})
           (supercontext, "section")

        """

        if isinstance(supercontext, tuple) or isinstance(supercontext, list):
            self._supercontext = supercontext

        elif isinstance(supercontext, self.__class__):
            self._supercontext = (supercontext, None)

        else:
            raise ValueError("supercontext must either be tuple or context object")

    @supercontext.deleter
    def supercontext(self):
        """
        Deletes context supercontext
        """

        self._supercontext = None

    def update_config_from_file(self, path: str) -> None:
        """
        Update config values from file

        :param path: config file path
        """

        config = read_config(path)
        self._config_values.update(config)

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

        supercontext_val = None

        for supercontext_tuple in reversed(self.supercontext):
            supercontext = supercontext_tuple[0]
            section = supercontext_tuple[1]

            # get value from supercontext if available
            if section is not None:
                supercontext_val_i = supercontext.get(section, None).get(name, None)

            else:
                supercontext_val_i = supercontext.get(name, None)

            if supercontext_val_i is not None:
                supercontext_val = supercontext_val_i

        if supercontext_val is not None:
            return supercontext_val

        return self._config_values[name] if name in self.get_config_names() else default

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

        return list(self._config_values.keys())

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

        if isinstance(context, Context):
            GLOBAL_SUPERCONTEXT.append(context)

        else:
            raise TypeError("Argument 'context' must be of type 'processor_tools.Context'")

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        del GLOBAL_SUPERCONTEXT[-1]


if __name__ == "__main__":
    pass
