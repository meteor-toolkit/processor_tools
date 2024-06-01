"""processor_tools.tests.test_setup_utils - tests for processor_tools.setup_utils module"""

import unittest
from typing import Optional
import os
import random
import string
import subprocess
import sys
import shutil


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


def create_test_package(path: str, package_name: str, setup_str: Optional[str]):
    """
    Creates test python package

    :param path: path of directory to write test package to
    :param package_name: name of package
    :param setup_str: content of setup.py file
    """

    module_path = os.path.join(path, package_name)   # directory of test package
    module_init_path = os.path.join(module_path, "__init__.py")
    setup_path = os.path.join(path, "setup.py")

    os.makedirs(module_path)

    if setup_str is None:
        setup_str = (""
                     "\nfrom setuptools import setup"
                     "\nsetup("
                     "\n\tname='"+package_name+"',"
                     "\n\tversion='1.0',"
                     "\n\tauthors=''"
                     "\n)")

    with open(setup_path, "w") as f:
        f.write(setup_str)

    with open(module_init_path, "w") as f:
        f.write("")


def install_package(package_path: str, editable=False):
    """
    Installs local python package

    :param package_path: package project directory path
    :param editable: (default: False) option to define if package should be installed in editable mode
    """
    cwd = os.getcwd()

    os.chdir(package_path)

    if editable:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "."])

    os.chdir(cwd)


def uninstall_package(package_name: str):
    """
    Uninstalls python package

    :param package_name: name of package to uninstall
    """

    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])


class TestSetupUserConfig(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

        self.package_name = "test"

        setup_str = ("from processor_tools.setup_utils import SetupUserConfigDevelop, SetupUserConfigInstall"
                     "\nfrom setuptools import setup"
                     "\n\nsetup("
                     "\n\tname='" + self.package_name + "',"
                     "\n\tcmdclass={"
                     "\n\t\t'develop': SetupUserConfigDevelop,"
                     "\n\t\t'install': SetupUserConfigInstall,"
                     "\n\t},"
                     "\n\tversion='1.0',"
                     "\n\tauthors=''"
                     "\n)\n")

        create_test_package(self.tmp_dir, self.package_name, setup_str=setup_str)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_run(self):
        install_package(self.tmp_dir)

        # test if config directories setup properly

        uninstall_package(self.package_name)


if __name__ == "__main__":
    unittest.main()
