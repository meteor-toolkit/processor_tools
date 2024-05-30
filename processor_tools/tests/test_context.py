"""processor.tests.test_context - tests for processor_tools.context"""

import unittest
from unittest.mock import patch
from processor_tools.context import Context


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestContext(unittest.TestCase):
    def test___init___None(self):
        context = Context()
        self.assertDictEqual(context._config_values, dict())

    def test___init__dict(self):
        input_dict = {"test": "value"}
        context = Context(input_dict)
        self.assertDictEqual(context._config_values, input_dict)

    @patch("processor_tools.context.read_config", return_value={"test": "value"})
    def test___init__path(self, mock_read_config):
        context = Context("path")
        self.assertDictEqual(context._config_values, {"test": "value"})
        mock_read_config.assert_called_once_with("path")

    def test_get_config_names(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        entry_list = context.get_config_names()

        self.assertCountEqual(entry_list, ["entry1", "entry2", "entry3", "entry4"])

    @patch("processor_tools.context.Context.get_config_names")
    def test_keys(self, mock_get_config_names):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        entry_list = context.keys()

        self.assertCountEqual(entry_list, mock_get_config_names.return_value)
        mock_get_config_names.assert_called_once()

    def test_get(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context.get("entry2")

        self.assertCountEqual(value, "value2")

    @patch("processor_tools.context.Context.get")
    def test___getitem__(self, mock_get):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context["entry2"]

        self.assertEqual(value, mock_get.return_value)

    def test___getitem___config_with_nested(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": {"subentry1": "subvalue1"},
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context["entry2"]["subentry1"]

        self.assertEqual(value, "subvalue1")

    def test_set(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        context.set("entry5", "value5")

        self.assertEqual(context._config_values["entry5"], "value5")

    def test___setitem__(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        context["entry5"] = "value5"

        self.assertEqual(context._config_values["entry5"], "value5")


if __name__ == "__main__":
    unittest.main()
