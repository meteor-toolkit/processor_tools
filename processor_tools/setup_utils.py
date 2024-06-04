"""processor_tools.setup_utils - utilities for package setup"""

import os
from setuptools.command.develop import develop
from setuptools.command.install import install
from typing import Callable, List, Dict, Any, Type, Union, Optional
import __main__
from processor_tools.config_io import build_configdir


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["CustomCmdClassUtils", "build_configdir_cmdclass"]


class CustomCmdClassUtils:
    """
    Class for creating custom install cmd classes for setup, such that they can run defined functions before or after package installation
    """

    def build_cmdclass(
        self,
        preinstall: Optional[Callable] = None,
        postinstall: Optional[Callable] = None,
        pre_args: Optional[List[Any]] = None,
        pre_kwargs: Optional[Dict[str, Any]] = None,
        post_args: Optional[List[Any]] = None,
        post_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Type[Union[install, develop]]]:
        """
        Function to build the cmdclass argument for `setuptools.setup` so that a custom function is ran before or after package installation

        :param preinstall: function to run before package installation
        :param postinstall: function to run after package installation
        :param pre_args: arguments for pre-installation function
        :param pre_kwargs: keyword arguments for pre-installation function
        :param post_args: arguments for post-installation function
        :param post_kwargs: keyword arguments for post-installation function
        :return: cmdclass argument for `setuptools.setup` - dictionary of custom setuptools commands as `{"install": custom_install, "develop": custom_develop}`
        """

        cmdclass_dict = {
            "install": self._build_setuptools_cmd(
                cmd=install,
                preinstall=preinstall,
                postinstall=postinstall,
                pre_args=pre_args,
                pre_kwargs=pre_kwargs,
                post_args=post_args,
                post_kwargs=post_kwargs,
            ),
            "develop": self._build_setuptools_cmd(
                cmd=develop,
                preinstall=preinstall,
                postinstall=postinstall,
                pre_args=pre_args,
                pre_kwargs=pre_kwargs,
                post_args=post_args,
                post_kwargs=post_kwargs,
            ),
        }

        return cmdclass_dict

    @staticmethod
    def _build_setuptools_cmd(
        cmd: Union[Type[install], Type[develop]],
        preinstall: Optional[Callable] = None,
        postinstall: Optional[Callable] = None,
        pre_args: Optional[List[Any]] = None,
        pre_kwargs: Optional[Dict[str, Any]] = None,
        post_args: Optional[List[Any]] = None,
        post_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Type[Union[install, develop]]:
        """
        Function to build custom setuptools commands, such that they can run defined functions before or after package installation

        :param cmd: setuptools command - either `setuptools.command.develop.develop` or `setuptools.command.develop.install`
        :param preinstall: function to run before package installation
        :param postinstall: function to run after package installation
        :param pre_args: arguments for pre-installation function
        :param pre_kwargs: keyword arguments for pre-installation function
        :param post_args: arguments for post-installation function
        :param post_kwargs: keyword arguments for post-installation function
        :return: custom setuptools command
        """

        # Define custom setuptools command
        class CustomCmdClass(cmd):  # type: ignore

            # setup class variables to store args and kwargs
            preinstall_args: Optional[List[Any]] = pre_args
            preinstall_kwargs: Optional[Dict[str, Any]] = pre_kwargs
            postinstall_args: Optional[List[Any]] = post_args
            postinstall_kwargs: Optional[Dict[str, Any]] = post_kwargs

            def run(self):
                """
                Overriding the standard setuptools command run method, adding preinstall and postinstall functions
                """

                # if preinstall defined run first
                if preinstall is not None:
                    preinstall(*self.preinstall_args, **self.preinstall_kwargs)

                # run standard install process
                install.run(self)

                # if postinstall defined run last
                if postinstall is not None:
                    postinstall(*self.postinstall_args, **self.postinstall_kwargs)

        return CustomCmdClass


def build_configdir_cmdclass(package_name, configs):
    """
    Build a cmdclass argument for `setuptools.setup` that initialises a directory of configuration files on after package installation.

    * For the standard `"install"` mode the configuration directory is `~/.<packagename>`
    * For develop mode (i.e. editable mode with `-e` flag) mode the configuration directory is `<package_project_directory>/.<packagename>`

    Skips running if directory already exists (for example if package has previously been installed).

    :param package_name: package name
    :param configs:
    :return: cmdclass argument for `setuptools.setup` that initialises configuration directory post-install
    """

    # define paths for config directories
    install_path = os.path.join(os.path.expanduser("~"), "." + package_name)

    # build custom command class
    cmdutil = CustomCmdClassUtils()
    configdir_cmdclass = cmdutil.build_cmdclass(
        postinstall=build_configdir,
        post_args=[install_path, configs],
        post_kwargs={"exists_skip": True},
    )

    # customise the function arguments in "develop" so it can dynamically identify the package directory to write to
    delattr(configdir_cmdclass["develop"], "postinstall_args")

    @property
    def postinstall_args(self):
        develop_path = os.path.join(
            os.path.dirname(__main__.__file__), "." + package_name
        )
        return [develop_path, configs]

    configdir_cmdclass["develop"].postinstall_args = postinstall_args

    return configdir_cmdclass


if __name__ == "__main__":
    pass
