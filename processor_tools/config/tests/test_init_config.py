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
        self.assertEqual(self.config_init.home_dir(), os.path.join("/home/user", ".config", "testpkg"))
        mock_expanduser.assert_called_once_with("~")

    def test_project_dir_default(self):
        result = self.config_init.project_dir()
        self.assertEqual(result, os.path.join(os.getcwd(), ".testpkg"))

    def test_project_dir_explicit_project_path(self):
        result = self.config_init.project_dir(project_path="/some/project")
        self.assertEqual(result, os.path.join("/some/project", ".testpkg"))

    def test_project_dir_base_file(self):
        base_file = "/some/project/mypackage/config.py"
        result = self.config_init.project_dir(base_file=base_file)
        self.assertEqual(result, os.path.abspath(os.path.join("/some","project", "mypackage", ".testpkg")))

    def test_project_dir_base_file_takes_precedence(self):
        result = self.config_init.project_dir(
            base_file="/some/project/mypackage/config.py",
            project_path="/other/path",
        )
        self.assertEqual(result, os.path.abspath(os.path.join("/some","project", "mypackage", ".testpkg")))


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
            config_directory=os.path.join(self.tmp_dir, "config")
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_init_creates_directory(self):
        self.config_init.init()
        self.assertTrue(os.path.isdir(self.config_init.get_config_directory()))

    def test_init_dict_template(self):
        self.config_init.init()
        path = self.config_init.get_config_directory()
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
        self.config_init.init()
        filepath = os.path.join(path, "from_callable.yaml")
        self.assertTrue(os.path.exists(filepath))
        with open(filepath) as f:
            self.assertEqual(f.read(), "computed: result\n")

    def test_init_exists_skip_true_preserves_existing(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, "from_dict.yaml")
        with open(filepath, "w") as f:
            f.write("user: edited\n")

        self.config_init.init(path=path, exists_skip=True)

        with open(filepath) as f:
            self.assertEqual(f.read(), "user: edited\n")

    def test_init_exists_skip_false_overwrites_existing(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, "from_dict.yaml")
        with open(filepath, "w") as f:
            f.write("user: edited\n")

        self.config_init.init(path=path, exists_skip=False)

        with open(filepath) as f:
            self.assertEqual(f.read(), "entry1: value1\n")

    def test_init_exists_skip_default_is_true(self):
        path = os.path.join(self.tmp_dir, "config")
        os.makedirs(path, exist_ok=True)
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
             patch("processor_tools.config.init_config.shutil.copyfile"):
            self.config_init.reset_config_directory()
            self.config_init.init()
            mock_makedirs.assert_called_once_with(os.path.join("/home/user", ".config", "testpkg"), exist_ok=True)


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


class TestGetConfigDirectory(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)
        self.config_init = ConfigInit(package_name="testpkg", configs={})

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_get_config_directory_file_exists_valid_path(self):
        """Test getting config directory when file exists with valid path"""
        config_dir = os.path.join(self.tmp_dir, "config")
        os.makedirs(config_dir)
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        
        self.config_init.config_directory_file_path = config_file
        with open(config_file, "w") as f:
            f.write(config_dir)
        
        result = self.config_init.get_config_directory()
        self.assertEqual(result, config_dir)

    def test_get_config_directory_file_exists_invalid_path(self):
        """Test getting config directory when file exists but path is invalid"""
        invalid_path = os.path.join(self.tmp_dir, "nonexistent")
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        
        self.config_init.config_directory_file_path = config_file
        with open(config_file, "w") as f:
            f.write(invalid_path)
        
        with patch("processor_tools.config.init_config.Warning"):
            result = self.config_init.get_config_directory()
            self.assertEqual(result, self.config_init.home_dir())

    def test_get_config_directory_file_not_exists(self):
        """Test getting config directory when file doesn't exist"""
        nonexistent_file = os.path.join(self.tmp_dir, "nonexistent_config_file.txt")
        self.config_init.config_directory_file_path = nonexistent_file
        
        with patch.object(self.config_init, "home_dir", return_value="/home/testuser/.config/testpkg"):
            result = self.config_init.get_config_directory()
            self.assertEqual(result, "/home/testuser/.config/testpkg")

    def test_get_config_directory_uses_default_file_path(self):
        """Test that default config_directory_file_path is used when none provided"""
        config_dir = os.path.join(self.tmp_dir, "config")
        os.makedirs(config_dir)
        
        # Create the default path structure
        default_parent = os.path.dirname(self.config_init.config_directory_file_path)
        os.makedirs(default_parent, exist_ok=True)
        
        with open(self.config_init.config_directory_file_path, "w") as f:
            f.write(config_dir)
        
        result = self.config_init.get_config_directory()
        self.assertEqual(result, config_dir)

    def test_get_config_directory_with_whitespace(self):
        """Test getting config directory with whitespace in stored path"""
        config_dir = os.path.join(self.tmp_dir, "config")
        os.makedirs(config_dir)
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        
        self.config_init.config_directory_file_path = config_file
        with open(config_file, "w") as f:
            f.write(f"  {config_dir}  \n")
        
        result = self.config_init.get_config_directory()
        self.assertEqual(result, config_dir)


class TestSetConfigDirectory(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)
        self.config_init = ConfigInit(package_name="testpkg", configs={})

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_set_config_directory_creates_directories(self):
        """Test that config directory is created if it doesn't exist"""
        config_dir = os.path.join(self.tmp_dir, "new_config")
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        self.config_init.config_directory_file_path = config_file
        
        self.config_init.set_config_directory(config_directory=config_dir)
        
        self.assertTrue(os.path.exists(config_dir))
        self.assertTrue(os.path.isdir(config_dir))

    def test_set_config_directory_creates_parent_directories(self):
        """Test that parent directories are created for config file path"""
        config_dir = os.path.join(self.tmp_dir, "config")
        config_file = os.path.join(self.tmp_dir, "nested", "dirs", "config_file.txt")
        self.config_init.config_directory_file_path = config_file
        
        self.config_init.set_config_directory(config_directory=config_dir)
        
        self.assertTrue(os.path.exists(os.path.dirname(config_file)))

    def test_set_config_directory_writes_file(self):
        """Test that config directory path is written to file"""
        config_dir = os.path.join(self.tmp_dir, "config")
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        self.config_init.config_directory_file_path = config_file
        
        self.config_init.set_config_directory(config_directory=config_dir)
        
        with open(config_file, "r") as f:
            written_dir = f.read()
        self.assertEqual(written_dir, config_dir)

    def test_set_config_directory_uses_explicit_config_directory_file_path(self):
        """Test that a manually overridden config_directory_file_path is used"""
        config_dir = os.path.join(self.tmp_dir, "config")
        new_config_file = os.path.join(self.tmp_dir, "new_config_file.txt")
        
        self.config_init.config_directory_file_path = new_config_file
        self.config_init.set_config_directory(config_directory=config_dir)
        
        self.assertEqual(self.config_init.config_directory_file_path, new_config_file)
        with open(new_config_file, "r") as f:
            self.assertEqual(f.read(), config_dir)

    def test_set_config_directory_uses_existing_config_directory(self):
        """Test that existing config directory is used when none provided"""
        config_dir = os.path.join(self.tmp_dir, "config")
        os.makedirs(config_dir)
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        
        # Pre-populate the config file with a directory
        with open(config_file, "w") as f:
            f.write(config_dir)
        
        self.config_init.config_directory_file_path = config_file
        self.config_init.set_config_directory(config_directory=None)
        
        with open(config_file, "r") as f:
            written_dir = f.read()
        self.assertEqual(written_dir, config_dir)

    def test_set_config_directory_uses_default_file_path(self):
        """Test that default config_directory_file_path is used when none provided"""
        config_dir = os.path.join(self.tmp_dir, "config")
        
        # Create necessary parent directory
        default_parent = os.path.dirname(self.config_init.config_directory_file_path)
        os.makedirs(default_parent, exist_ok=True)
        
        self.config_init.set_config_directory(config_directory=config_dir)
        
        with open(self.config_init.config_directory_file_path, "r") as f:
            written_dir = f.read()
        self.assertEqual(written_dir, config_dir)

    def test_set_config_directory_does_not_overwrite_existing_config_dir(self):
        """Test that existing config directory is not removed when setting path"""
        config_dir = os.path.join(self.tmp_dir, "config")
        test_file = os.path.join(config_dir, "test.txt")
        config_file = os.path.join(self.tmp_dir, "config_file.txt")
        
        # Create config directory with existing file
        os.makedirs(config_dir)
        with open(test_file, "w") as f:
            f.write("test content")
        
        self.config_init.config_directory_file_path = config_file
        self.config_init.set_config_directory(config_directory=config_dir)
        
        # Verify existing file is preserved
        self.assertTrue(os.path.exists(test_file))
        with open(test_file, "r") as f:
            self.assertEqual(f.read(), "test content")


if __name__ == "__main__":
    unittest.main()