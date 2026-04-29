"""processor_tools.config_io - reading/writing config files"""

import os
import shutil
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
import configparser


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["read_config", "write_config", "build_configdir", "find_config"]


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

        # Check int
        is_int = True
        try:
            int(val)
        except:
            is_int = False

        if is_int:
            return int

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

        with open(path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False)


class ConfigIOFactory:
    """
    Class to return config file reader/writer object suitable for given config file formats, supports:

    * default python (with file extensions `["config", "cfg", "conf"]`) - read only
    * yaml file (with file extensions `["yml", "yaml"]`)

    Can be extended to include more file formats in future
    """

    # Configuration file readers by extension - maintain with new readers
    READER_BY_EXT = {
        "config": ConfigReader(),
        "cfg": ConfigReader(),
        "conf": ConfigReader(),
        "yml": YAMLReader(),
        "yaml": YAMLReader(),
    }

    WRITER_BY_EXT = {"yml": YAMLWriter(), "yaml": YAMLWriter()}

    def get_reader(self, path: str) -> BaseConfigReader:
        """
        Return config reader for file with given file extension

        :param path: config file path
        :return: config reader
        """

        ext = self._get_file_extension(path)

        if ext not in self.READER_BY_EXT.keys():
            raise ValueError("Invalid file extension: " + ext)

        return self.READER_BY_EXT[ext]

    def get_writer(self, path: str) -> BaseConfigWriter:
        """
        Return config writer for file with given file extension

        :param path: config file path
        :return: config writer
        """

        ext = self._get_file_extension(path)

        if ext not in self.WRITER_BY_EXT.keys():
            raise ValueError("Invalid file extension: " + ext)

        return self.WRITER_BY_EXT[ext]

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


def build_configdir(
    path, configs: Dict[str, Union[str, dict]], exists_skip: bool = False
):
    """
    Writes set of configuration files to defined directory

    :param path: configuration directory path (created if doesn't exist)
    :param configs: definition of configuration files as a dictionary, with an entry per configuration file to write - where the key should be the filename to write and the value should define the file content (see below for options of doing this).
    :param exists_skip: (default: False) option to bypass processing if path directory already exists

    Configs entry options:

    * path of config file to copy to configuration directory
    * configuration values dictionary

    For example:

    .. code-block:: python

       configs = {
           "copied_config.yaml": "path/to/old_config.yaml",
           "new_config.yaml": {"entry1": "value1"}
       }

    """

    # skip process if config directory exists and chosen to exists_skip
    if os.path.isdir(path) and exists_skip:
        return

    os.makedirs(path, exist_ok=True)

    for filename, config_def in configs.items():
        filepath = os.path.join(path, filename)

        if isinstance(config_def, str):
            shutil.copyfile(config_def, filepath)

        elif isinstance(config_def, dict):
            write_config(filepath, config_def)


def find_config(path) -> List[str]:
    """
    Returns configuration files in directory (i.e. files that can be read by :py:class:`read_config <processor_tools.read_config>`).

    :param path: directory containing configuration files
    """

    config_paths = []

    conf_fact = ConfigIOFactory()

    for filename in os.listdir(path):
        filename_ext = conf_fact._get_file_extension(filename)

        if filename_ext in conf_fact.READER_BY_EXT.keys():
            config_paths.append(os.path.join(path, filename))

    return config_paths


if __name__ == "__main__":
    pass
