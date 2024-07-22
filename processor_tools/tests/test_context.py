"""processor.tests.test_context - tests for processor_tools.context"""

import shutil
import unittest
from unittest.mock import patch, call
import os
import random
import string
from processor_tools import GLOBAL_SUPERCONTEXT
from processor_tools.context import Context, set_global_supercontext


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestContext(unittest.TestCase):
    def test___init___None_default_None(self):
        context = Context()
        self.assertDictEqual(context._config_values, dict())
        self.assertIsNone(context._supercontext)

    def test___init__dict_default_None(self):
        input_dict = {"test": "value"}
        context = Context(input_dict)
        self.assertDictEqual(context._config_values, input_dict)
        self.assertIsNone(context._supercontext)

    @patch("processor_tools.context.read_config", return_value={"test": "value"})
    def test___init__filepath_default_None(self, mock_read_config):
        context = Context("path")
        self.assertDictEqual(context._config_values, {"test": "value"})
        self.assertIsNone(context._supercontext)
        mock_read_config.assert_called_once_with("path")

    @patch("processor_tools.context.Context.update_config_from_file")
    def test___init__filepath_default_filepath(self, mock_update):
        Context.default_config = "path2"
        context = Context("path")

        exp_calls = [call("path2"), call("path")]

        Context.default_config = None
        mock_update.assert_has_calls(exp_calls)

    @patch("processor_tools.context.Context.update_config_from_file")
    def test___init__filepath_default_list_filepath(self, mock_update):
        Context.default_config = ["path2", "path3"]
        context = Context("path")

        exp_calls = [call("path3"), call("path2"), call("path")]

        Context.default_config = None
        mock_update.assert_has_calls(exp_calls)

    @patch("processor_tools.context.find_config", return_value=["found_path"])
    @patch("processor_tools.context.Context.update_config_from_file")
    def test___init__filepath_default_dir(self, mock_update, mock_find):
        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        Context.default_config = tmp_dir
        context = Context("path")

        exp_calls = [call("found_path"), call("path")]

        Context.default_config = None
        mock_find.assert_called_once_with(tmp_dir)
        mock_update.assert_has_calls(exp_calls)

        shutil.rmtree(tmp_dir)

    @patch("processor_tools.context.find_config", return_value=["found_path"])
    @patch("processor_tools.context.Context.update_config_from_file")
    def test___init__filepath_default_default_list_mixed(self, mock_update, mock_find):
        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        Context.default_config = [tmp_dir, "path2"]
        context = Context("path")

        exp_calls = [call("path2"), call("found_path"), call("path")]

        mock_find.assert_called_once_with(tmp_dir)
        mock_update.assert_has_calls(exp_calls)

        Context.default_config = None
        shutil.rmtree(tmp_dir)

    def test_supercontext_setter_context(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()
        context.supercontext = supercontext

        self.assertTrue(isinstance(context._supercontext, tuple))
        self.assertTrue(isinstance(context._supercontext[0], Context))
        self.assertDictEqual(context._supercontext[0]._config_values, supercontext._config_values)
        self.assertIsNone(context._supercontext[1])

    def test_supercontext_del(self):
        context = Context()
        context._supercontext = Context({"section": {"val1": 1, "val2": 2}})

        del context.supercontext

        self.assertIsNone(context._supercontext)

    def test_supercontext_setter_tuple(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()
        context.supercontext = (supercontext, "section")

        self.assertTrue(isinstance(context._supercontext, tuple))
        self.assertTrue(isinstance(context._supercontext[0], Context))
        self.assertDictEqual(context._supercontext[0]._config_values, supercontext._config_values)
        self.assertEqual(context._supercontext[1], "section")

    def test_supercontext_getter(self):
        context = Context()
        context._supercontext = (Context({"section": {"val1": 1, "val2": 2}}), "section")

        self.assertTrue(isinstance(context.supercontext, list))
        self.assertEqual(len(context.supercontext), 1)
        self.assertTrue(isinstance(context.supercontext[0], tuple))
        self.assertTrue(isinstance(context.supercontext[0][0], Context))
        self.assertDictEqual(context.supercontext[0][0]._config_values, context._supercontext[0]._config_values)
        self.assertEqual(context.supercontext[0][1], "section")

    @patch("processor_tools.context.GLOBAL_SUPERCONTEXT", [(Context({"val1": 1, "val2": 2}), None)])
    def test_supercontext_getter_global(self):
        context = Context()
        context._supercontext = (Context({"section": {"val1": 1, "val2": 2}}), "section")

        self.assertTrue(isinstance(context.supercontext, list))
        self.assertEqual(len(context.supercontext), 2)

        self.assertTrue(isinstance(context.supercontext[0], tuple))
        self.assertTrue(isinstance(context.supercontext[0][0], Context))
        self.assertDictEqual(context.supercontext[0][0]._config_values, {"val1": 1, "val2": 2})
        self.assertIsNone(context.supercontext[0][1])

        self.assertTrue(isinstance(context.supercontext[1], tuple))
        self.assertTrue(isinstance(context.supercontext[1][0], Context))
        self.assertDictEqual(context.supercontext[1][0]._config_values, context._supercontext[0]._config_values)
        self.assertEqual(context.supercontext[1][1], "section")

    @patch("processor_tools.context.GLOBAL_SUPERCONTEXT", [(Context({"val1": 1, "val2": 2}), None)])
    def test_supercontext_getter_global_only(self):
        context = Context()

        self.assertTrue(isinstance(context.supercontext, list))
        self.assertEqual(len(context.supercontext), 1)

        self.assertTrue(isinstance(context.supercontext[0], tuple))
        self.assertTrue(isinstance(context.supercontext[0][0], Context))
        self.assertDictEqual(context.supercontext[0][0]._config_values, {"val1": 1, "val2": 2})
        self.assertIsNone(context.supercontext[0][1])

    def test___init___supercontext_context(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context(supercontext=supercontext)

        self.assertTrue(isinstance(context._supercontext, tuple))
        self.assertTrue(isinstance(context._supercontext[0], Context))
        self.assertDictEqual(context._supercontext[0]._config_values, supercontext._config_values)
        self.assertIsNone(context._supercontext[1])

    def test___init___supercontext_tuple(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context(supercontext=(supercontext, "section"))

        self.assertTrue(isinstance(context._supercontext, tuple))
        self.assertTrue(isinstance(context._supercontext[0], Context))
        self.assertDictEqual(context._supercontext[0]._config_values, supercontext._config_values)
        self.assertEqual(context._supercontext[1], "section")

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

    def test_get_super1(self):
        context = Context()
        context.supercontext = Context({"entry2": 2})

        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context.get("entry2")

        self.assertEqual(value, 2)

    def test_get_super1_section(self):
        context = Context()
        context.supercontext = (Context({"section": {"entry2": 2}}), "section")

        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        value = context.get("entry2")

        self.assertEqual(value, 2)

    def test_get_super2(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        context._supercontext = [
            (Context({"section": {"entry1": 1}}), "section"),
            (Context({"section": {"entry2": 2}}), "section")
        ]

        self.assertEqual(context.get("entry1"), 1)
        self.assertEqual(context.get("entry2"), 2)

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


class TestSetGlobalSupercontext(unittest.TestCase):

    def test_function_call(self):

        context = Context({"val": 1})
        set_global_supercontext(context)

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], Context))
        self.assertDictEqual(GLOBAL_SUPERCONTEXT[0]._config_values, {"val": 1})

    def test_function_call_invalid(self):

        self.assertRaises(TypeError, set_global_supercontext, "hello")

    def test_with(self):

        context = Context({"val": 1})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)
        with set_global_supercontext(context):

            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], Context))
            self.assertDictEqual(GLOBAL_SUPERCONTEXT[0]._config_values, {"val": 1})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)

    def test_with_nested(self):

        context1 = Context({"val1": 1})
        context2 = Context({"val2": 2})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)
        with set_global_supercontext(context1):

            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], Context))
            self.assertDictEqual(GLOBAL_SUPERCONTEXT[0]._config_values, {"val1": 1})

            with set_global_supercontext(context2):

                self.assertEqual(len(GLOBAL_SUPERCONTEXT), 2)
                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], Context))
                self.assertDictEqual(GLOBAL_SUPERCONTEXT[0]._config_values, {"val1": 1})
                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[1], Context))
                self.assertDictEqual(GLOBAL_SUPERCONTEXT[1]._config_values, {"val2": 2})

            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], Context))
            self.assertDictEqual(GLOBAL_SUPERCONTEXT[0]._config_values, {"val1": 1})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)


if __name__ == "__main__":
    unittest.main()
