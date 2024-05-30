"""processor.context - customer container from processing state"""


from typing import Optional, Any, List, Union
from processor_tools import read_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["Context"]


class Context:
    """
    Class to determine and store processing state

    :param config: processing configuration data, either:

    * dictionary of configuration data
    * path of configuration file, or list of paths (earlier in the list overwrites later in the list
    """

    DEFAULT_CONFIG_PATH: Optional[str] = None

    def __init__(self, config: Optional[Union[str, List[str], dict]] = None) -> None:
        self._config_values = {}

        # open default config values
        if self.DEFAULT_CONFIG_PATH is not None:
            self.update_config_from_file(self.DEFAULT_CONFIG_PATH)

        # update default config with user defined values
        if config is not None:
            if isinstance(config, dict):
                self._config_values.update(config)

            elif isinstance(config, str):
                config = [config]

            if isinstance(config, list):
                for c in reversed(config):
                    self.update_config_from_file(c)

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
