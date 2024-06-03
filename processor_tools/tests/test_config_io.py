"""processor_tools.tests.test_config_io - tests for processor_tools.config_io module"""

import unittest
import random
import string
import shutil
from unittest.mock import patch
import os
from configparser import RawConfigParser
from processor_tools.config_io import (
    BaseConfigReader,
    ConfigReader,
    YAMLReader,
    YAMLWriter,
    ConfigIOFactory,
    read_config,
    write_config
)


this_directory = os.path.dirname(__file__)


def create_config_file(fname, values=None):
    config = RawConfigParser()

    if values is None:
        values = {"entry1": "value1", "entry2": "value2"}

    config["Default"] = values

    with open(fname, "w") as configfile:
        config.write(configfile)

    return None


class TestBaseConfigReader(unittest.TestCase):
    def test__infer_dtype_str(self):
        dtype = BaseConfigReader._infer_dtype("string")
        self.assertEqual(dtype, str)

    def test__infer_dtype_float(self):
        dtype = BaseConfigReader._infer_dtype("11.7")
        self.assertEqual(dtype, float)

    def test__infer_dtype_bool_True(self):
        dtype = BaseConfigReader._infer_dtype("False")
        self.assertEqual(dtype, bool)

    def test__infer_dtype_bool_False(self):
        dtype = BaseConfigReader._infer_dtype("False")
        self.assertEqual(dtype, bool)


class TestConfigReader(unittest.TestCase):
    def setUp(self) -> None:
        self.config = RawConfigParser()
        self.config["Default"] = {"entry1": "value1", "entry2": "value2"}
        self.config["Other"] = {"entry3": "value3", "entry4": "value4"}

    def test__extract_config_value_empty_string(self):
        config = RawConfigParser()
        config["section"] = {"key": ""}

        val = ConfigReader._extract_config_value(config, "section", "key")
        self.assertIsNone(val)

    def test__extract_config_value_None(self):
        config = RawConfigParser()
        config["section"] = {"key": None}

        val = ConfigReader._extract_config_value(config, "section", "key")
        self.assertIsNone(val)

    def test__extract_config_value_None_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": None}

        val = ConfigReader._extract_config_value(config, "section", "key", dtype=bool)
        self.assertEqual(val, False)

    def test__extract_config_value_dtype_None(self):
        config = RawConfigParser()
        config["section"] = {"key": "val"}

        val = ConfigReader._extract_config_value(config, "section", "key")
        self.assertEqual(val, "val")

    def test__extract_config_value_dtype_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": "False"}

        val = ConfigReader._extract_config_value(config, "section", "key")
        self.assertEqual(val, False)

    def test__extract_config_value_int(self):
        config = RawConfigParser()
        config["section"] = {"key": 3}

        val = ConfigReader._extract_config_value(config, "section", "key", dtype=int)
        self.assertEqual(type(val), int)
        self.assertEqual(val, 3)

    def test__extract_config_value_bool(self):
        config = RawConfigParser()
        config["section"] = {"key": "True"}

        val = ConfigReader._extract_config_value(config, "section", "key", dtype=bool)
        self.assertEqual(type(val), bool)
        self.assertEqual(val, True)

    def test__extract_config_value_float(self):
        config = RawConfigParser()
        config["section"] = {"key": 2.0}

        val = ConfigReader._extract_config_value(config, "section", "key", dtype=float)
        self.assertEqual(type(val), float)
        self.assertEqual(val, 2.0)

    def test_read(self):
        fname = "file2.config"
        config_values = {"entry1": "value1"}

        create_config_file(fname, config_values)

        reader = ConfigReader()
        config = reader.read(fname)

        self.assertEqual(type(config), dict)
        self.assertEqual(config["Default"]["entry1"], "value1")

        os.remove(fname)


class TestYAMLReaderFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

        yml_str = "test:\n" "   entry1: value1\n" "   entry2: false\n" "   entry3: 1.2"

        self.exp_config = {"test": {"entry1": "value1", "entry2": False, "entry3": 1.2}}

        self.yml_path = os.path.join(self.tmp_dir, "test.yaml")

        with open(self.yml_path, "w") as f:
            f.write(yml_str)

    def test_read(self):
        reader = YAMLReader()
        config = reader.read(self.yml_path)

        self.assertEqual(type(config), dict)
        self.assertDictEqual(config, self.exp_config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)


class TestYAMLWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = "tmp_" + "".join(random.choices(string.ascii_lowercase, k=6))
        os.makedirs(self.tmp_dir)

    def test_write(self):
        yml_path = os.path.join(self.tmp_dir, "test.yaml")
        config_dict = {"test": {"entry1": "value1", "entry2": False, "entry3": 1.2}}

        writer = YAMLWriter()
        writer.write(yml_path, config_dict)

        self.assertTrue(os.path.exists(yml_path))

        with open(yml_path, "r") as f:
            yml_str = f.read()

        exp_yml_str = "test:\n" "  entry1: value1\n" "  entry2: false\n" "  entry3: 1.2\n"

        self.assertEqual(yml_str, exp_yml_str)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)


class TestConfigIOFactory(unittest.TestCase):
    def test_get_reader_config(self):
        crf = ConfigIOFactory()
        self.assertEqual(
            type(crf.get_reader("test/file/path.config")), type(ConfigReader())
        )

    def test_get_reader_yaml(self):
        crf = ConfigIOFactory()
        self.assertEqual(
            type(crf.get_reader("test/file/path.yaml")), type(YAMLReader())
        )

    def test_get_writer_yaml(self):
        crf = ConfigIOFactory()
        self.assertEqual(
            type(crf.get_writer("test/file/path.yaml")), type(YAMLWriter())
        )

    def test_get_reader_invalid(self):
        crf = ConfigIOFactory()
        self.assertRaises(ValueError, crf.get_reader, "test/file/path.invalid")

    def test_get_file_extension(self):
        path = "test/file/path.extension"
        self.assertEqual(ConfigIOFactory._get_file_extension(path), "extension")


class ReadConfFactory(unittest.TestCase):
    @patch("processor_tools.config_io.ConfigIOFactory")
    def test_read_config(self, mock_reader):
        cfg = read_config("test.path")
        mock_reader.return_value.get_reader.assert_called_once_with("test.path")
        mock_reader.return_value.get_reader.return_value.read.assert_called_once_with(
            "test.path"
        )

        self.assertEqual(
            cfg, mock_reader.return_value.get_reader.return_value.read.return_value
        )


class WriteConfFactory(unittest.TestCase):
    @patch("processor_tools.config_io.ConfigIOFactory")
    def test_write_config(self, mock_reader):
        cfg = write_config("test.path", "dict")
        mock_reader.return_value.get_writer.assert_called_once_with("test.path")
        mock_reader.return_value.get_writer.return_value.write.assert_called_once_with(
            "test.path", "dict"
        )

        self.assertEqual(
            cfg, mock_reader.return_value.get_writer.return_value.write.return_value
        )


if __name__ == "__main__":
    unittest.main()
