"""processor_tools.tests.test_setup_utils - tests for processor_tools.setup_utils module"""

import unittest
from unittest.mock import patch, call
from typing import Optional
import os
import random
import string
import subprocess
import sys
import shutil
from setuptools.command.develop import develop
from setuptools.command.install import install
from processor_tools.config_io import build_configdir
from processor_tools.setup_utils import CustomCmdClassUtils, build_configdir_cmdclass


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


"""___Helper Functions___"""


def create_test_package(path: str, package_name: str, setup_str: Optional[str]):
    """
    Creates test python package

    :param path: path of directory to write test package to
    :param package_name: name of package
    :param setup_str: content of setup.py file
    """

    module_path = os.path.join(path, package_name)  # directory of test package
    module_init_path = os.path.join(module_path, "__init__.py")
    setup_path = os.path.join(path, "setup.py")

    os.makedirs(module_path)

    if setup_str is None:
        setup_str = (
            ""
            "\nfrom setuptools import setup"
            "\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)"
        )

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

    subprocess.check_call(
        [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
    )


"""___Test Classes___"""


class TestCustomCmdClassUtils(unittest.TestCase):
    def test__build_setuptools_cmd_install_preinstall_postinstall(self):

        # this is the key test that proves custom command classes are working, everything else mocks this use
        # of this function

        tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(tmp_dir)

        package_name = "test"

        # define a setup.py that builds a custom cmdclass with:
        # * a preinstall function the writes a file "file1.txt" with content "hello"
        # * a postinstall function the writes a file "file2.txt" with content "goodbye"

        file1_path = os.path.join(os.path.abspath(tmp_dir), "file1.txt")
        file1_content = "hello"
        file2_path = os.path.join(os.path.abspath(tmp_dir), "file2.txt")
        file2_content = "goodbye"

        setup_str = (
            "from processor_tools.setup_utils import CustomCmdClassUtils"
            "\nfrom setuptools.command.install import install"
            "\nfrom setuptools import setup"
            "\n\n\ndef test_func(path, content):"
            "\n\twith open(path, 'w+') as f:"
            "\n\t\tf.write(content)"
            "\n\n\ncmd_utils = CustomCmdClassUtils()"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass={"
            "\n\t\t'install': cmd_utils._build_setuptools_cmd("
            "\n\t\t\tinstall,"
            "\n\t\t\tpreinstall=test_func,"
            "\n\t\t\tpre_args=['" + file1_path + "'],"
            "\n\t\t\tpre_kwargs={'content': '" + file1_content + "'},"
            "\n\t\t\tpostinstall=test_func,"
            "\n\t\t\tpost_args=['" + file2_path + "'],"
            "\n\t\t\tpost_kwargs={'content': '" + file2_content + "'},"
            "\n\t\t)"
            "\n\t},"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        create_test_package(tmp_dir, package_name, setup_str=setup_str)

        install_package(tmp_dir)

        # test file1 created correctly preinstall
        self.assertTrue(os.path.exists(file1_path))
        with open(file1_path, "r") as f:
            file1_line = f.read()
        self.assertEqual(file1_content, file1_line)

        # test file2 created correctly postinstall
        self.assertTrue(os.path.exists(file2_path))
        with open(file2_path, "r") as f:
            file2_line = f.read()
        self.assertEqual(file2_content, file2_line)

        uninstall_package(package_name)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)

    def test__build_setuptools_cmd_install_preinstall_only(self):

        # this is the key test that proves custom command classes are working, everything else mocks this use
        # of this function

        tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(tmp_dir)

        package_name = "test"

        # define a setup.py that builds a custom cmdclass with:
        # * a preinstall function the writes a file "file1.txt" with content "hello"

        file1_path = os.path.join(os.path.abspath(tmp_dir), "file1.txt")
        file1_content = "hello"

        setup_str = (
            "from processor_tools.setup_utils import CustomCmdClassUtils"
            "\nfrom setuptools.command.install import install"
            "\nfrom setuptools import setup"
            "\n\n\ndef test_func(path, content):"
            "\n\twith open(path, 'w+') as f:"
            "\n\t\tf.write(content)"
            "\n\n\ncmd_utils = CustomCmdClassUtils()"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass={"
            "\n\t\t'install': cmd_utils._build_setuptools_cmd("
            "\n\t\t\tinstall,"
            "\n\t\t\tpreinstall=test_func,"
            "\n\t\t\tpre_args=['" + file1_path + "'],"
            "\n\t\t\tpre_kwargs={'content': '" + file1_content + "'},"
            "\n\t\t)"
            "\n\t},"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        create_test_package(tmp_dir, package_name, setup_str=setup_str)

        install_package(tmp_dir)

        # test file1 created correctly preinstall
        self.assertTrue(os.path.exists(file1_path))
        with open(file1_path, "r") as f:
            file1_line = f.read()
        self.assertEqual(file1_content, file1_line)

        uninstall_package(package_name)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)

    def test__build_setuptools_cmd_install_postinstall_only(self):

        # this is the key test that proves custom command classes are working, everything else mocks this use
        # of this function

        tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(tmp_dir)

        package_name = "test"

        # define a setup.py that builds a custom cmdclass with:
        # * a postinstall function the writes a file "file2.txt" with content "goodbye"

        file2_path = os.path.join(os.path.abspath(tmp_dir), "file2.txt")
        file2_content = "goodbye"

        setup_str = (
            "from processor_tools.setup_utils import CustomCmdClassUtils"
            "\nfrom setuptools.command.install import install"
            "\nfrom setuptools import setup"
            "\n\n\ndef test_func(path, content):"
            "\n\twith open(path, 'w+') as f:"
            "\n\t\tf.write(content)"
            "\n\n\ncmd_utils = CustomCmdClassUtils()"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass={"
            "\n\t\t'install': cmd_utils._build_setuptools_cmd("
            "\n\t\t\tinstall,"
            "\n\t\t\tpostinstall=test_func,"
            "\n\t\t\tpost_args=['" + file2_path + "'],"
            "\n\t\t\tpost_kwargs={'content': '" + file2_content + "'},"
            "\n\t\t)"
            "\n\t},"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        create_test_package(tmp_dir, package_name, setup_str=setup_str)

        install_package(tmp_dir)

        # test file2 created correctly postinstall
        self.assertTrue(os.path.exists(file2_path))
        with open(file2_path, "r") as f:
            file2_line = f.read()
        self.assertEqual(file2_content, file2_line)

        uninstall_package(package_name)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)

    def test__build_setuptools_cmd_develop_preinstall_postinstall(self):

        # this is the key test that proves custom command classes are working, everything else mocks this use
        # of this function

        tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(tmp_dir)

        package_name = "test"

        # define a setup.py that builds a custom cmdclass with:
        # * a preinstall function the writes a file "file1.txt" with content "hello"
        # * a postinstall function the writes a file "file2.txt" with content "goodbye"

        file1_path = os.path.join(os.path.abspath(tmp_dir), "file1.txt")
        file1_content = "hello"
        file2_path = os.path.join(os.path.abspath(tmp_dir), "file2.txt")
        file2_content = "goodbye"

        setup_str = (
            "from processor_tools.setup_utils import CustomCmdClassUtils"
            "\nfrom setuptools.command.develop import develop"
            "\nfrom setuptools import setup"
            "\n\n\ndef test_func(path, content):"
            "\n\twith open(path, 'w+') as f:"
            "\n\t\tf.write(content)"
            "\n\n\ncmd_utils = CustomCmdClassUtils()"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass={"
            "\n\t\t'develop': cmd_utils._build_setuptools_cmd("
            "\n\t\t\tdevelop,"
            "\n\t\t\tpreinstall=test_func,"
            "\n\t\t\tpre_args=['" + file1_path + "'],"
            "\n\t\t\tpre_kwargs={'content': '" + file1_content + "'},"
            "\n\t\t\tpostinstall=test_func,"
            "\n\t\t\tpost_args=['" + file2_path + "'],"
            "\n\t\t\tpost_kwargs={'content': '" + file2_content + "'},"
            "\n\t\t)"
            "\n\t},"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        create_test_package(tmp_dir, package_name, setup_str=setup_str)

        install_package(tmp_dir, editable=True)

        # test file1 created correctly preinstall
        self.assertTrue(os.path.exists(file1_path))
        with open(file1_path, "r") as f:
            file1_line = f.read()
        self.assertEqual(file1_content, file1_line)

        # test file2 created correctly postinstall
        self.assertTrue(os.path.exists(file2_path))
        with open(file2_path, "r") as f:
            file2_line = f.read()
        self.assertEqual(file2_content, file2_line)

        uninstall_package(package_name)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)

    @patch(
        "processor_tools.setup_utils.CustomCmdClassUtils._build_setuptools_cmd",
        side_effect=["install", "develop"],
    )
    def test_build_cmdclass(self, mock_build):
        cmd_util = CustomCmdClassUtils()

        cmdclass = cmd_util.build_cmdclass(
            preinstall="pre_func",
            pre_args="pre_args",
            pre_kwargs="pre_kwargs",
            postinstall="post_func",
            post_args="post_args",
            post_kwargs="post_kwargs",
        )

        self.assertCountEqual(cmdclass.keys(), ["install", "develop"])
        self.assertEqual(cmdclass["install"], "install")
        self.assertEqual(cmdclass["develop"], "develop")

        for call, setuptools_cmd in zip(mock_build.mock_calls, [install, develop]):
            self.assertDictEqual(
                call.kwargs,
                {
                    "cmd": setuptools_cmd,
                    "preinstall": "pre_func",
                    "pre_args": "pre_args",
                    "pre_kwargs": "pre_kwargs",
                    "postinstall": "post_func",
                    "post_args": "post_args",
                    "post_kwargs": "post_kwargs",
                },
            )


class TestBuildConfigDirCmdClass(unittest.TestCase):
    @patch("processor_tools.config_io.os.path.expanduser", return_value="test")
    @patch(
        "processor_tools.setup_utils.CustomCmdClassUtils._build_setuptools_cmd",
        side_effect=[
            CustomCmdClassUtils._build_setuptools_cmd(install),
            CustomCmdClassUtils._build_setuptools_cmd(develop),
        ],
    )
    def test_build_configdir_cmdclass(self, mock_build, mock_expand):

        package_name = "test_package"
        configs = {"copied_config.yaml": "path/to/old_config.yaml"}
        configdir_cmdclass = build_configdir_cmdclass(package_name, configs)

        exp_mock_build_calls = [
            call(
                cmd=install,
                preinstall=None,
                postinstall=build_configdir,
                pre_args=None,
                pre_kwargs=None,
                post_args=[os.path.join("test", "." + package_name)],
                post_kwargs={"configs": configs, "exists_skip": True},
            ),
            call(
                cmd=develop,
                preinstall=None,
                postinstall=build_configdir,
                pre_args=None,
                pre_kwargs=None,
                post_args=[os.path.join("test", "." + package_name)],
                post_kwargs={"configs": configs, "exists_skip": True},
            ),
        ]

        mock_build.assert_has_calls(exp_mock_build_calls)

    def test__build_configdir_cmdclass_install(self):

        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        package_name = "test_package"

        package_dir = os.path.join(tmp_dir, package_name)
        os.makedirs(package_dir)

        config_dir = os.path.abspath(os.path.join(tmp_dir, "config"))

        # define a setup.py that builds configdir cmdclass

        setup_str = (
            "from processor_tools.setup_utils import build_configdir_cmdclass"
            "\nfrom setuptools import setup"
            "\n\n\ncmdclass = build_configdir_cmdclass('"
            + package_name
            + "', {'file1.yaml': {'entry1': 'value1'}})"
            "\ncmdclass['install'].postinstall_args[0]= '" + config_dir + "'"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass=cmdclass,"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        # create, install, uninstall test package
        create_test_package(package_dir, package_name, setup_str=setup_str)

        install_package(package_dir)

        uninstall_package(package_name)

        # test config file created correctly postinstall
        configfile_path = os.path.join(config_dir, "file1.yaml")
        self.assertTrue(os.path.exists(configfile_path))

        with open(configfile_path, "r") as f:
            configfile_line = f.read()
        self.assertEqual("entry1: value1\n", configfile_line)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)

    def test__build_configdir_cmdclass_develop(self):
        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        package_name = "test_package"

        package_dir = os.path.join(tmp_dir, package_name)
        os.makedirs(package_dir)

        config_dir = os.path.abspath(os.path.join(tmp_dir, "config"))

        # define a setup.py that builds configdir cmdclass

        setup_str = (
            "from processor_tools.setup_utils import build_configdir_cmdclass"
            "\nfrom setuptools import setup"
            "\n\n\ncmdclass = build_configdir_cmdclass('"
            + package_name
            + "', {'file1.yaml': {'entry1': 'value1'}})"
            "\n\n\nsetup("
            "\n\tname='" + package_name + "',"
            "\n\tcmdclass=cmdclass,"
            "\n\tversion='1.0',"
            "\n\tauthors=''"
            "\n)\n"
        )

        # create, install, uninstall test package
        create_test_package(package_dir, package_name, setup_str=setup_str)

        install_package(package_dir, editable=True)

        uninstall_package(package_name)

        # test config file created correctly postinstall
        configfile_path = os.path.join(package_dir, "." + package_name, "file1.yaml")
        self.assertTrue(os.path.exists(configfile_path))

        with open(configfile_path, "r") as f:
            configfile_line = f.read()
        self.assertEqual("entry1: value1\n", configfile_line)

        # to see what package is created and installed comment this line, so it is not removed after test is run
        shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
