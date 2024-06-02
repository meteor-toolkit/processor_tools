"""processor_tools.setup_utils - utilities for package setup"""

from setuptools.command.develop import develop
from setuptools.command.install import install
from typing import Callable, List, Dict, Any, Type, Union, Optional


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = ["CustomCmdClassUtils"]


class CustomCmdClassUtils:
    """
    Class for creating custom install cmd classes for setup, such that they can run defined functions before or after package installation
    """

    def build_setup_cmdclass(
            self,
            cmd: Union[Type[install], Type[develop]],
            preinstall: Optional[Callable] = None,
            postinstall: Optional[Callable] = None,
            pre_args: Optional[List[Any]] = None,
            pre_kwargs: Optional[Dict[str, Any]] = None,
            post_args: Optional[List[Any]] = None,
            post_kwargs: Optional[Dict[str, Any]] = None
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
        class CustomCmdClass(cmd):

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


if __name__ == "__main__":
    pass
