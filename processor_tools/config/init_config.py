"""processor_tools.config.init_config - config directory initialisation"""

import argparse
import os
import shutil
from typing import Callable, Dict, List, Union
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

    def __init__(self, package_name: str, configs: Dict[str, Union[str, dict, Callable]]):
        self.package_name = package_name
        self.configs = configs

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

        :param path: config directory to write files into. Defaults to
            :py:meth:`home_dir`.
        :param exists_skip: if ``True`` (default), skip any file that already exists,
            preserving user edits. Set to ``False`` to overwrite.
        """

        if path is None:
            path = self.home_dir()

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

    def missing(self, path: str = None) -> List[str]:
        """
        Return a list of config filenames not present in the given directory.

        :param path: config directory to check. Defaults to :py:meth:`home_dir`.
        """

        if path is None:
            path = self.home_dir()

        return [
            filename
            for filename in self.configs
            if not os.path.exists(os.path.join(path, filename))
        ]

    def is_initialised(self, path: str = None) -> bool:
        """
        Return ``True`` if all defined config files are present in the given directory.

        :param path: config directory to check. Defaults to :py:meth:`home_dir`.
        """

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

        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite files that already exist",
        )

        args = parser.parse_args()

        if args.path:
            path = args.path
        elif args.project:
            path = self.project_dir()
        else:
            path = self.home_dir()

        self.init(path=path, exists_skip=not args.overwrite)
        print(f"Config initialised at {path}")


if __name__ == "__main__":
    pass
