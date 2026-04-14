"""processor_tools.tests.test_init_config - tests for processor_tools.config.init_config module"""

import os
import random
import shutil
import string
import unittest
from unittest.mock import call, patch

from processor_tools.config.init_config import ConfigInit


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


class TestConfigInitDirs(unittest.TestCase):
    def setUp(self):
        self.config_init = ConfigInit(package_name="testpkg", configs={})

    @patch("processor_tools.config.init_config.os.path.expanduser", return_value="/home/user")
    def test_home_dir(self, mock_expanduser):
        self.assertEqual(self.config_init.home_dir(), "/home/user/.testpkg")
        mock_expanduser.assert_called_once_with("~")

    def test_project_dir_default(self):
        result = self.config_init.project_dir()
        self.assertEqual(result, os.path.join(os.getcwd(), ".testpkg"))

    def test_project_dir_explicit_project_path(self):
        result = self.config_init.project_dir(project_path="/some/project")
        self.assertEqual(result, "/some/project/.testpkg")

    def test_project_dir_base_file(self):
        base_file = "/some/project/mypackage/config.py"
        result = self.config_init.project_dir(base_file=base_file)
        self.assertEqual(result, os.path.join("/some/project/mypackage", ".testpkg"))

    def test_project_dir_base_file_takes_precedence(self):
        result = self.config_init.project_dir(
            base_file="/some/project/mypackage/config.py",
            project_path="/other/path",
        )
        self.assertEqual(result, os.path.join("/some/project/mypackage", ".testpkg"))


class TestConfigInitInit(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

        self.src_yaml = os.path.join(self.tmp_dir, "source.yaml")
        with open(self.src_yaml, "w") as f:
            f.write("key: value\n")

        self.config_init = ConfigInit(
            package_name="testpkg",
            configs={
                "from_dict.yaml": {"entry1": "value1"},
                "from_file.yaml": self.src_yaml,
                "from_callable.yaml": lambda: {"computed": "result"},
            },
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_init_creates_directory(self):
        path = os.path.join(self.tmp_dir, "config")
        self.config_init.init(path=path)
        self.assertTrue(os.path.isdir(path))

    def test_init_dict_template(self):
        path = os.path.join(self.tmp_dir, "config")
        self.config_init.init(path=path)
        filepath = os.path.join(path, "from_dict.yaml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            self.assertEqual(f.read(), "entry1: value1\n")

    def test_init_file_template(self):
        path = os.path.join(self.tmp_dir, "config")
        self.config_init.init(path=path)
        filepath = os.path.join(path, "from_file.yaml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            self.assertEqual(f.read(), "key: value\n")

    def test_init_callable_template(self):
        path = os.path.join(self.tmp_dir, "config")
        self.config_init.init(path=path)
        filepath = os.path.join(path, "from_callable.yaml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            self.assertEqual(f.read(), "computed: result\n")

    def test_init_exists_skip_true_preserves_existing(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path)
        filepath = os.path.join(path, "from_dict.yaml")
        with open(filepath, "w") as f:
            f.write("user: edited\n")

        self.config_init.init(path=path, exists_skip=True)

        with open(filepath) as f:
            self.assertEqual(f.read(), "user: edited\n")

    def test_init_exists_skip_false_overwrites_existing(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path)
        filepath = os.path.join(path, "from_dict.yaml")
        with open(filepath, "w") as f:
            f.write("user: edited\n")

        self.config_init.init(path=path, exists_skip=False)

        with open(filepath) as f:
            self.assertEqual(f.read(), "entry1: value1\n")

    def test_init_exists_skip_default_is_true(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path)
        filepath = os.path.join(path, "from_dict.yaml")
        with open(filepath, "w") as f:
            f.write("user: edited\n")

        self.config_init.init(path=path)

        with open(filepath) as f:
            self.assertEqual(f.read(), "user: edited\n")

    @patch("processor_tools.config.init_config.os.path.expanduser", return_value="/home/user")
    def test_init_defaults_to_home_dir(self, mock_expanduser):
        with patch("processor_tools.config.init_config.os.makedirs") as mock_makedirs, \
             patch("processor_tools.config.init_config.write_config"), \
             patch("processor_tools.config.init_config.shutil.copyfile"), \
             patch("processor_tools.config.init_config.os.path.exists", return_value=True):
            self.config_init.init()
            mock_makedirs.assert_called_once_with("/home/user/.testpkg", exist_ok=True)


class TestConfigInitMissing(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

        self.config_init = ConfigInit(
            package_name="testpkg",
            configs={
                "file1.yaml": {"entry1": "value1"},
                "file2.yaml": {"entry2": "value2"},
            },
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_missing_all(self):
        result = self.config_init.missing(path=self.tmp_dir)
        self.assertCountEqual(result, ["file1.yaml", "file2.yaml"])

    def test_missing_some(self):
        with open(os.path.join(self.tmp_dir, "file1.yaml"), "w") as f:
            f.write("")
        result = self.config_init.missing(path=self.tmp_dir)
        self.assertEqual(result, ["file2.yaml"])

    def test_missing_none(self):
        for filename in ["file1.yaml", "file2.yaml"]:
            with open(os.path.join(self.tmp_dir, filename), "w") as f:
                f.write("")
        result = self.config_init.missing(path=self.tmp_dir)
        self.assertEqual(result, [])


class TestConfigInitIsInitialised(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

        self.config_init = ConfigInit(
            package_name="testpkg",
            configs={"file1.yaml": {"entry1": "value1"}},
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_is_initialised_false(self):
        self.assertFalse(self.config_init.is_initialised(path=self.tmp_dir))

    def test_is_initialised_true(self):
        with open(os.path.join(self.tmp_dir, "file1.yaml"), "w") as f:
            f.write("")
        self.assertTrue(self.config_init.is_initialised(path=self.tmp_dir))


if __name__ == "__main__":
    unittest.main()