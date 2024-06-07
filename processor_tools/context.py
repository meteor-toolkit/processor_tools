"""processor.context - customer container from processing state"""

import os.path
from typing import Optional, Dict, Any, List, Union
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
    """

    # default_config class variable enables you to set configuration file(s)/directory(ies) of files that are
    # loaded every time the class is initialised. Configuration values from these files come lower in the priority
    # list than those defined at init.
    default_config: Optional[Union[str, List[str]]] = None

    def __init__(self, config: Optional[Union[str, List[str], dict]] = None) -> None:
        self._config_values: Dict[str, Any] = {}

        # init default config path
        if self.default_config is None:
            default_config_paths = []
        elif isinstance(self.default_config, str):
            default_config_paths = [self.default_config]
        else:
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


if __name__ == "__main__":
    pass
