"""processor.context - customer container from processing state"""

import os.path
from typing import Optional, Dict, Any, List, Union, Tuple
from copy import deepcopy
from pydantic.utils import deep_update
from processor_tools import GLOBAL_SUPERCONTEXT
from processor_tools import read_config, find_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["Context", "set_global_supercontext", "clear_global_supercontext"]


class Context:
    """
    Class to determine and store processing state

    :param config: processing configuration data, either:

    * dictionary of configuration data
    * path of configuration file or directory containing set of configuration files
    * list of dicts/paths (earlier in the list overwrites later in the list)

    :param supercontext: context supercontext or list of supercontexts (earlier in the list overwrites later in the list), configuration values of which override those defined in the context. Each defined as context object or tuple of:

    * `supercontext` (*Context*) - supercontext object
    * `section` (*str*) -  name of section of supercontext to apply as supercontext

    For example:

    .. code-block:: python

       supercontext = Context({"section": {"val1": 1 , "val2", 2}})
       (supercontext, "section")
    """

    # default_config class variable enables you to set configuration file(s)/directory(ies) of files that are
    # loaded every time the class is initialised. Configuration values from these files/dicts come lower in the priority
    # list than those defined at init.
    default_config: Optional[Union[str, List[str]]] = None

    def __init__(
        self,
        config: Optional[Union[str, List[str], dict]] = None,
        supercontext: Optional[List[Union["Context", Tuple["Context", str]]]] = None,
    ) -> None:

        # initialise attributes
        self._config_values: Dict[str, Any] = {}
        self._supercontext: List[Tuple["Context", Union[None, str]]] = []

        if supercontext is not None:
            self.supercontext = supercontext

        # init default config definitions
        if self.default_config is None:
            default_config = []
        elif isinstance(self.default_config, str) or isinstance(
            self.default_config, dict
        ):
            default_config = [self.default_config]
        else:
            default_config = self.default_config

        if not isinstance(default_config, list):
            raise TypeError(
                "class attribute `default_config` must be one of types [`str`, `dict`, `list[str | dict]`]"
            )

        # init user config definitions
        if config is None:
            init_config = []
        elif isinstance(config, str) or isinstance(config, dict):
            init_config = [config]
        else:
            init_config = config

        if not isinstance(init_config, list):
            raise TypeError(
                "argument `config` must be one of types [`str`, `dict`, `list[str | dict]`]"
            )

        configs = init_config + default_config

        # open config paths
        for config_i in reversed(configs):
            if isinstance(config_i, str):
                if os.path.isdir(config_i):
                    for p in find_config(config_i):
                        self.update_from_file(p, skip_if_not_exists=True)

                else:
                    self.update_from_file(config_i, skip_if_not_exists=True)

            elif isinstance(config_i, dict):
                self.update(config_i)

            else:
                raise TypeError("config definition must be of type [`str`, `dict`]")

    @property
    def supercontext(self) -> List[Tuple["Context", Union[None, str]]]:
        """
        Return context supercontexts

        :return: supercontexts
        """

        return self._supercontext if self._supercontext != [] else None

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
            raise TypeError(
                "'supercontext' must be defined as one of type [`processor_tools.Context`, `tuple`, `list`]"
            )

        for i, supercontext_i in enumerate(supercontext):
            if isinstance(supercontext_i, self.__class__):
                supercontext[i] = (supercontext_i, None)

            elif isinstance(supercontext_i, tuple):
                if not (
                    isinstance(supercontext_i[0], self.__class__)
                    and (
                        isinstance(supercontext_i[1], str)
                        or (supercontext_i[1] is None)
                    )
                ):
                    raise TypeError(
                        "supercontext tuple must be of type `(processor_tools.Context, str | None)`"
                    )

            else:
                raise TypeError(
                    "supercontext definition must be either `processor_tools.Context` or  `(processor_tools.Context, str | None)`"
                )

        self._supercontext = supercontext

    @supercontext.deleter
    def supercontext(self):
        """
        Deletes context supercontexts
        """

        self._supercontext = []

    def update_from_file(self, path: str, skip_if_not_exists: bool = False) -> None:
        """
        Update config values from file

        :param path: config file path
        :param skip_if_not_exists: skips running if file at path doesn't exist
        """

        if os.path.exists(path):
            config = read_config(path)
            self._config_values = deep_update(self._config_values, config)

        else:
            if skip_if_not_exists:
                pass
            else:
                raise ValueError("no such file: " + path)

    def update(self, config: dict) -> None:
        """
        Update config values

        :param config: dictionary of configuration data
        """
        self._config_values = deep_update(self._config_values, config)

    @property
    def config_values(self) -> Any:
        """
        Returns defined configuration values

        :return: configuration values
        """

        config_values = self._config_values

        if (self.supercontext is not None) or (GLOBAL_SUPERCONTEXT != []):
            config_values = deepcopy(self._config_values)

        if self.supercontext is not None:
            config_values = self._update_with_supercontexts(
                config_values, self.supercontext
            )

        if GLOBAL_SUPERCONTEXT != []:
            config_values = self._update_with_supercontexts(
                config_values, GLOBAL_SUPERCONTEXT
            )

        return config_values

    def _update_with_supercontexts(self, config_values, supercontexts):

        for supercontext_tuple_i in reversed(supercontexts):
            supercontext_i = supercontext_tuple_i[0]
            section_i = supercontext_tuple_i[1]

            # get value from supercontext if available
            if section_i is not None:
                supercontext_values_i = supercontext_i.get(section_i, None)

            else:
                supercontext_values_i = supercontext_i._config_values

            if supercontext_values_i is not None:
                config_values = deep_update(config_values, supercontext_values_i)

            if supercontext_i.supercontext is not None:
                config_values = self._update_with_supercontexts(
                    config_values, supercontext_i.supercontext
                )

        return config_values

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

    :param context: supercontext defined as context object or tuple of:

        * `supercontext` (*Context*) - supercontext object
        * `section` (*str*) -  name of section of supercontext to apply as supercontext

    For example:

    .. code-block:: python

       supercontext = Context({"section": {"val1": 1 , "val2", 2}})
       (supercontext, "section")

    Can be run with a `with` statement, as follows

    .. code-block:: python

       from processor_tools import Context, set_global_supercontext

       my_context = Context()
       with set_global_supercontext(my_context):
           run_process()

    In this example, `my_context` is set as the global supercontext within the scope of the `with` statement and then removed after.
    """

    def __init__(self, supercontext: Union[Tuple[Context, str], Context]):
        self(supercontext)

    def __call__(self, supercontext: Union[Tuple[Context, str], Context]):

        if isinstance(supercontext, Context):
            supercontext = (supercontext, None)

        elif isinstance(supercontext, tuple):
            if not (
                isinstance(supercontext[0], Context)
                and (isinstance(supercontext[1], str) or (supercontext[1] is None))
            ):
                raise TypeError(
                    "supercontext tuple must be of type `(processor_tools.Context, str | None)`"
                )

        if isinstance(supercontext, tuple):
            GLOBAL_SUPERCONTEXT.append(supercontext)

        else:
            raise TypeError(
                "Argument 'context' must be of type 'processor_tools.Context'"
            )

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        del GLOBAL_SUPERCONTEXT[-1]


def clear_global_supercontext():
    """
    Unsets all global supercontexts
    """

    GLOBAL_SUPERCONTEXT.clear()


if __name__ == "__main__":
    pass
