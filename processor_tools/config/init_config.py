"""processor_tools.config.init_config - config directory initialisation"""

import argparse
import os
import shutil
from typing import Callable, Dict, List, Optional, Union
from processor_tools.config.config_io import write_config


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["ConfigInit"]


class ConfigInit:
    """
    Defines and initialises a set of configuration files for a package.

    Config filenames are specified relative to a config directory whose location is
    resolved at init time. Two standard locations are provided:

    * :py:meth:`home_dir` — ``~/.<package_name>`` (user home, default)
    * :py:meth:`project_dir` — ``<project_path>/.<package_name>``

    An explicit path can also be passed directly to :py:meth:`init`.

    :param package_name: package name, used to derive the standard config directory
        names
    :param configs: dict mapping config filename to its template. Template can be:

        * ``dict`` — written as a new config file with those values
        * ``str`` — path to an existing file that is copied to the target location
        * ``callable`` — called at init time with no arguments, must return a ``dict``

    Example::

        config_init = ConfigInit(
            package_name="mypackage",
            configs={
                "settings.yaml": {"db_host": "localhost", "debug": False},
                "logging.yaml": "/path/to/default_logging.yaml",
                "env.yaml": lambda: {"hostname": os.uname().nodename},
            },
        )

        config_init.init()                                    # -> ~/.<package_name>/
        config_init.init(config_init.project_dir())          # -> <cwd>/.<package_name>/
        config_init.init(config_init.project_dir(__file__))  # -> <this file's dir>/.<package_name>/
        config_init.init("/explicit/path")                    # -> /explicit/path/
    """

    def __init__(self, package_name: str, configs: Dict[str, Union[str, dict, Callable]], config_directory: str = None, config_directory_file_path: str = None):
        """
        Initialise the ConfigInit instance.
        :param package_name: package name, used to derive the standard config directory
        :param configs: dict mapping config filename to its template. Template can be:
            * ``dict`` — written as a new config file with those values
            * ``str`` — path to an existing file that is copied to the target location
            * ``callable`` — called at init time with no arguments, must return a ``dict``
        :param config_directory: optional config directory path (i.e. path where the config files will be stored). If not provided, defaults to the path string stored in the config_directory_file_path.
        :param config_directory_file_path: optional path to the config directory file (i.e. path to the file which stores the config_directory path). If not provided, defaults to ``~/.<processor_tools>/config_directory_<package_name>.txt``."""
        self.package_name = package_name
        self.configs = configs
        if config_directory_file_path is not None:
            self.config_directory_file_path = config_directory_file_path
        else:
            self.config_directory_file_path = os.path.join(os.path.expanduser("~"), ".processor_tools", f"{self.package_name}_config_directory.txt")
        
        config_directory = config_directory if config_directory is not None else self.get_config_directory()
        if config_directory=="home":
            config_directory = self.home_dir()
        if config_directory=="project":
            config_directory = self.project_dir()        
        self.set_config_directory(config_directory) 

    def get_config_directory(self) -> str:
        """
        Get the config directory path from the config directory file, or return the default home directory if the file does not exist.

        :return: config directory path
        """
        if os.path.exists(self.config_directory_file_path):
            with open(self.config_directory_file_path, "r") as f:
                config_directory = f.read().strip()
                if config_directory=="" or not os.path.exists(config_directory):
                    Warning(f"Config directory path {f.read().strip()} from {self.config_directory_file_path} does not exist. Defaulting to home directory.")
                    config_directory = self.home_dir()
        else:
            config_directory = self.home_dir()
        
        return config_directory

    def set_config_directory(self, config_directory: Optional[str] = None):
        """
        Set the config directory path in the config directory file.

        :param config_directory: config directory path to set
        """
        if config_directory is None:
            config_directory = self.get_config_directory()

        if not os.path.exists(config_directory):
            os.makedirs(config_directory, exist_ok=True)

        if not os.path.exists(os.path.dirname(self.config_directory_file_path)):
            os.makedirs(os.path.dirname(self.config_directory_file_path), exist_ok=True)
        
        with open(self.config_directory_file_path, "w") as f:
            f.write(config_directory)

    def reset_config_directory(self):
        """
        Reset the config directory by deleting the config directory file and all config files in the config directory.
        """
        config_directory = self.get_config_directory()

        if os.path.exists(config_directory):
            shutil.rmtree(config_directory)

        if os.path.exists(self.config_directory_file_path):
            os.remove(self.config_directory_file_path)

    def home_dir(self) -> str:
        """
        Return the standard user-home config directory: ``~/.<package_name>``.
        """

        return os.path.join(os.path.expanduser("~"), f".{self.package_name}")

    def project_dir(self, base_file: str = None, project_path: str = None) -> str:
        """
        Return the standard project config directory: ``<base>/.<package_name>``.

        Passing ``base_file=__file__`` from the calling module gives a deterministic
        path regardless of the working directory.

        :param base_file: path to a file whose directory is used as the base (e.g.
            ``__file__`` from the calling module). Takes precedence over
            ``project_path``.
        :param project_path: explicit base directory. Defaults to the current working
            directory if neither argument is given.
        """

        if base_file is not None:
            base = os.path.dirname(os.path.abspath(base_file))
        elif project_path is not None:
            base = project_path
        else:
            base = os.getcwd()

        return os.path.join(base, f".{self.package_name}")

    def init(self, path: str = None, exists_skip: bool = True):
        """
        Create all defined config files in the given directory.

        The directory is created automatically if it does not exist.

        :param path: path to the directory where config files will be created. Defaults to the path returned by :py:meth:`get_config_directory`.
        :param exists_skip: if ``True`` (default), skip any file that already exists,
            preserving user edits. Set to ``False`` to overwrite.
        """
        if path is None:
            path = self.get_config_directory()
        os.makedirs(path, exist_ok=True)

        for filename, template in self.configs.items():
            filepath = os.path.join(path, filename)

            if exists_skip and os.path.exists(filepath):
                continue

            if callable(template):
                template = template()

            if isinstance(template, str):
                shutil.copyfile(template, filepath)
            elif isinstance(template, dict):
                write_config(filepath, template)
    
    def list_config(self, path: str = None) -> List[str]:
        """
        Return a list of config filenames present in the given directory.

        :param path: path to the directory where config files are expected. Defaults to the path returned by :py:meth:`get_config_directory`.
        :return: list of config filenames present in the directory
        """
        if path is None:
            path = self.get_config_directory()

        return [
            filename
            for filename in self.configs
            if os.path.exists(os.path.join(path, filename))
        ]

    def missing(self, path: str = None) -> List[str]:
        """
        Return a list of config filenames not present in the given directory.

        """
        if path is None:
            path = self.get_config_directory()

        return [
            filename
            for filename in self.configs
            if not os.path.exists(os.path.join(path, filename))
        ]

    def is_initialised(self, path: str = None) -> bool:
        """
        Return ``True`` if all defined config files are present in the given directory.

        """
        if path is None:
            path = self.get_config_directory()

        return len(self.missing(path)) == 0

    def cli(self):
        """
        Command-line interface for initialising the config directory.

        Intended to be wired up as a ``console_scripts`` entry point in the consuming
        package::

            # in mypackage/config.py
            config_init = ConfigInit(package_name="mypackage", configs={...})

            def init_cli():
                config_init.cli()

            # in pyproject.toml
            [project.scripts]
            mypackage-init = "mypackage.config:init_cli"

        Flags:

        * ``--project``        use the project config directory (``<cwd>/.<package_name>``)
          instead of the user home directory
        * ``--path PATH``      write to an explicit directory (mutually exclusive with
          ``--project``)
        * ``--overwrite``      overwrite files that already exist
        """

        parser = argparse.ArgumentParser(
            description=f"Initialise config directory for {self.package_name}."
        )

        location = parser.add_mutually_exclusive_group()
        location.add_argument(
            "--project",
            action="store_true",
            help=f"write to project config directory (<cwd>/.{self.package_name})",
        )
        location.add_argument(
            "--path",
            metavar="PATH",
            help="write to an explicit directory path",
        )
        location.add_argument(
            "--home",
            action="store_true",
            help=f"write to user home config directory (~/.{self.package_name})",
        )

        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite files that already exist",
        )

        args = parser.parse_args()


        if args.path:
            self.set_config_directory(config_directory=args.path)
        elif args.project:
            self.set_config_directory(config_directory=self.project_dir())
        else:
            self.set_config_directory(config_directory=self.home_dir())

        path = self.get_config_directory()

        self.init(exists_skip=not args.overwrite)
        print(f"Config initialised at {path}")


if __name__ == "__main__":
    pass
