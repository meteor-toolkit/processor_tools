"""processor_tools.config_io - reading/writing config files"""

import os
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union
import configparser


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["read_config", "write_config"]


class BaseConfigReader(ABC):
    """
    Base class for config file readers.

    Implementations should infer types of values and convert to appropriate python objects for the following:

    * floats -- "1" -> float(1)
    * bools -- "true" -> bool(True)
    """

    @abstractmethod
    def read(self, path: str) -> Dict:
        """
        Returns information from configuration file

        :param path: path of configuration file
        :return: configuration values dictionary
        """

        pass

    @staticmethod
    def _infer_dtype(val: Any) -> type:
        """
        Return inferred dtype of val

        :param val: value
        :return: inferred data type
        """

        if val is None:
            return type(None)

        # Check bool
        if (val.lower() == "true") or (val.lower() == "false"):
            return bool

        # Check float
        is_float = True
        try:
            float(val)
        except:
            is_float = False

        if is_float:
            return float

        return str


class ConfigReader(BaseConfigReader):
    """
    Default python config file reader
    """

    def read(self, path: str) -> Dict:
        """
        Returns information from configuration file

        :param path: path of configuration file
        :return: configuration values dictionary
        """

        config_values: Dict = dict()

        # Allows handling of relative paths to path
        cwd = os.getcwd()
        path = os.path.abspath(path)
        config_directory = os.path.dirname(path)

        os.chdir(config_directory)
        config = configparser.RawConfigParser()
        config.read(path)

        for section in config.sections():
            config_values[section] = dict()
            for key in config[section].keys():
                config_values[section][key] = self._extract_config_value(
                    config, section, key
                )

        os.chdir(cwd)
        return config_values

    @staticmethod
    def _extract_config_value(
        config: configparser.RawConfigParser,
        section: str,
        key: str,
        dtype: Optional[type] = None,
    ) -> Union[None, str, bool, int, float]:
        """
        Return value from config file

        :param config: parsed config file
        :param section: section to retrieve data from
        :param key: key in section to retrieve data from
        :param dtype: type of data to return

        :return: config value
        """

        val = config.get(section, key, fallback=None)

        dtype = ConfigReader._infer_dtype(val) if dtype is None else dtype

        if (val == "") or (val is None):
            if dtype == bool:
                return False
            return None

        if dtype == str:
            if Path(val).exists():
                val = os.path.abspath(val)

            return val

        elif dtype == bool:
            return config.getboolean(section, key)

        elif dtype == int:
            return config.getint(section, key)

        elif dtype == float:
            return config.getfloat(section, key)

        else:
            return None


class YAMLReader(BaseConfigReader):
    """
    YAML file reader
    """

    def read(self, path: str) -> Dict:
        """
        Returns information from yaml file

        :param path: path of yaml file
        :return: configuration values dictionary
        """

        with open(path, "r") as stream:
            config_values = yaml.safe_load(stream)

        return config_values


class BaseConfigWriter(ABC):
    """
    Base class for config file writers.
    """

    @abstractmethod
    def write(self, path: str, config_dict: dict):
        """
        Writes information to configuration file

        :param path: path of configuration file
        :param config_dict: configuration values dictionary
        """

        pass


class YAMLWriter(BaseConfigWriter):
    """
    YAML file writer
    """

    def write(self, path: str, config_dict: dict):
        """
        Writes information to yaml file

        :param path: path of yaml file
        :param config_dict: configuration values dictionary
        """

        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)


class ConfigIOFactory:
    """
    Class to return config file reader/writer object suitable for given config file formats, supports:

    * default python (with file extensions `["config", "cfg", "conf"]`) - read only
    * yaml file (with file extensions `["yml", "yaml"]`)

    Can be extended to include more file formats in future
    """

    def get_reader(self, path: str) -> BaseConfigReader:
        """
        Return config reader for file with given file extension

        :param path: config file path
        :return: config reader
        """

        ext = self._get_file_extension(path)

        if ext in ["config", "cfg", "conf"]:
            return ConfigReader()

        elif ext in ["yml", "yaml"]:
            return YAMLReader()

        else:
            raise ValueError("Invalid file extension: " + ext)

    def get_writer(self, path: str) -> BaseConfigWriter:
        """
        Return config writer for file with given file extension

        :param path: config file path
        :return: config writer
        """

        ext = self._get_file_extension(path)

        if ext in ["yml", "yaml"]:
            return YAMLWriter()

        else:
            raise ValueError("Invalid file extension: " + ext)

    @staticmethod
    def _get_file_extension(path: str) -> str:
        """
        Return file extension for file path

        :param path: file path
        :return: file extension
        """

        return os.path.splitext(path)[1][1:]


def read_config(path: str) -> dict:
    """
    Read configuration file, supported file types:

    * default python
    * yaml

    Ensures strings, floats and booleans are returned in the correct Python types.

    :param path: configuration file path
    :return: configuration values dictionary
    """

    # get correct reader
    factory = ConfigIOFactory()
    reader = factory.get_reader(path)

    return reader.read(path)


def write_config(path: str, config_dict: dict):
    """
    Write configuration file, supported file types:

    * yaml

    :param path: configuration file path
    :param config_dict: configuration values dictionary
    """

    # get correct reader
    factory = ConfigIOFactory()
    writer = factory.get_writer(path)

    return writer.write(path, config_dict)


if __name__ == "__main__":
    pass
