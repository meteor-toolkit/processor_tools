"""processor.tests.test_context - tests for processor_tools.context"""

import shutil
import unittest
from unittest.mock import patch, call, PropertyMock
import os
import random
import string
from processor_tools import GLOBAL_SUPERCONTEXT
from processor_tools.context import (
    Context,
    set_global_supercontext,
    clear_global_supercontext,
)


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"


class TestContext(unittest.TestCase):
    def test___init___None_default_None(self):
        context = Context()
        self.assertDictEqual(context._config_values, dict())
        self.assertEqual(context._supercontext, [])

    def test___init__dict_default_None(self):
        input_dict = {"test": "value"}
        context = Context(input_dict)
        self.assertDictEqual(context._config_values, input_dict)
        self.assertEqual(context._supercontext, [])

    @patch("processor_tools.context.read_config", return_value={"test": "value"})
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_None(self, mock_read_config, mock_exists):
        context = Context("path")
        self.assertDictEqual(context._config_values, {"test": "value"})
        self.assertEqual(context._supercontext, [])
        mock_read_config.assert_called_once_with("path")

    @patch("processor_tools.context.Context.update_from_file")
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_filepath(self, mock_exists, mock_update):
        Context.default_config = "path2"
        context = Context("path")

        exp_calls = [call("path2", skip_if_not_exists=True), call("path", skip_if_not_exists=True)]

        Context.default_config = None
        mock_update.assert_has_calls(exp_calls)

    @patch("processor_tools.context.Context.update_from_file")
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_list_filepath(self, mock_exists, mock_update):
        Context.default_config = ["path2", "path3"]
        context = Context("path")

        exp_calls = [call("path3", skip_if_not_exists=True), call("path2", skip_if_not_exists=True), call("path", skip_if_not_exists=True)]

        Context.default_config = None
        mock_update.assert_has_calls(exp_calls)

    @patch("processor_tools.context.Context.update")
    @patch("processor_tools.context.Context.update_from_file")
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_list_filepath_dict(self, mock_exists, mock_updatef, mock_update):
        Context.default_config = ["path2", "path3", {"entry": "val"}]
        context = Context("path")

        exp_calls = [call("path3", skip_if_not_exists=True), call("path2", skip_if_not_exists=True),
                     call("path", skip_if_not_exists=True)]

        Context.default_config = None
        mock_updatef.assert_has_calls(exp_calls)
        mock_update.assert_called_once_with({"entry": "val"})

    @patch("processor_tools.context.find_config", return_value=["found_path"])
    @patch("processor_tools.context.Context.update_from_file")
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_dir(self, mock_exists, mock_update, mock_find):
        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        Context.default_config = tmp_dir
        context = Context("path")

        exp_calls = [call("found_path", skip_if_not_exists=True), call("path", skip_if_not_exists=True)]

        Context.default_config = None
        mock_find.assert_called_once_with(tmp_dir)
        mock_update.assert_has_calls(exp_calls)

        shutil.rmtree(tmp_dir)

    @patch("processor_tools.context.find_config", return_value=["found_path"])
    @patch("processor_tools.context.Context.update_from_file")
    @patch("processor_tools.context.os.path.exists", return_value=True)
    def test___init__filepath_default_default_list_mixed(self, mock_exists, mock_update, mock_find):
        random_string = random.choices(string.ascii_lowercase, k=6)
        tmp_dir = "tmp_" + "".join(random_string)
        os.makedirs(tmp_dir)

        Context.default_config = [tmp_dir, "path2"]
        context = Context("path")

        exp_calls = [call("path2", skip_if_not_exists=True), call("found_path", skip_if_not_exists=True), call("path", skip_if_not_exists=True)]

        mock_find.assert_called_once_with(tmp_dir)
        mock_update.assert_has_calls(exp_calls)

        Context.default_config = None
        shutil.rmtree(tmp_dir)

    def test_supercontext_setter_context(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()
        context.supercontext = supercontext

        self.assertTrue(isinstance(context._supercontext, list))
        self.assertTrue(isinstance(context._supercontext[0], tuple))
        self.assertTrue(isinstance(context._supercontext[0][0], Context))
        self.assertDictEqual(
            context._supercontext[0][0]._config_values, supercontext._config_values
        )
        self.assertIsNone(context._supercontext[0][1])

    def test_supercontext_setter_tuple(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()
        context.supercontext = (supercontext, "section")

        self.assertTrue(isinstance(context._supercontext, list))
        self.assertTrue(isinstance(context._supercontext[0], tuple))
        self.assertTrue(isinstance(context._supercontext[0][0], Context))
        self.assertDictEqual(
            context._supercontext[0][0]._config_values, supercontext._config_values
        )
        self.assertEqual(context._supercontext[0][1], "section")

    def test_supercontext_setter_bad_tuple(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()

        with self.assertRaises(TypeError):
            context.supercontext = (supercontext, 1)

    def test_supercontext_setter_invalidtype(self):
        supercontext = "hello"

        context = Context()

        with self.assertRaises(TypeError):
            context.supercontext = supercontext

    def test_supercontext_setter_list(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context()
        context.supercontext = [(supercontext, "section"), supercontext]

        self.assertTrue(isinstance(context._supercontext, list))

        self.assertTrue(isinstance(context._supercontext[0], tuple))
        self.assertTrue(isinstance(context._supercontext[0][0], Context))
        self.assertDictEqual(
            context._supercontext[0][0]._config_values, supercontext._config_values
        )
        self.assertEqual(context._supercontext[0][1], "section")

        self.assertTrue(isinstance(context._supercontext[1], tuple))
        self.assertTrue(isinstance(context._supercontext[1][0], Context))
        self.assertDictEqual(
            context._supercontext[1][0]._config_values, supercontext._config_values
        )
        self.assertIsNone(context._supercontext[1][1])

    def test_supercontext_setter_list_invalidtype(self):
        supercontext = ["hello"]

        context = Context()

        with self.assertRaises(TypeError):
            context.supercontext = supercontext

    def test_supercontext_del(self):
        context = Context()
        context._supercontext = Context({"section": {"val1": 1, "val2": 2}})

        del context.supercontext

        self.assertEqual(context._supercontext, [])

    def test_supercontext_getter(self):
        context = Context()
        context._supercontext = [
            (Context({"section": {"val1": 1, "val2": 2}}), "section")
        ]

        self.assertTrue(isinstance(context.supercontext, list))
        self.assertEqual(len(context.supercontext), 1)
        self.assertTrue(isinstance(context.supercontext[0], tuple))
        self.assertTrue(isinstance(context.supercontext[0][0], Context))
        self.assertDictEqual(
            context.supercontext[0][0]._config_values,
            context._supercontext[0][0]._config_values,
        )
        self.assertEqual(context.supercontext[0][1], "section")

    def test___init___supercontext_context(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context(supercontext=supercontext)

        self.assertTrue(isinstance(context._supercontext, list))

        self.assertTrue(isinstance(context._supercontext[0], tuple))
        self.assertTrue(isinstance(context._supercontext[0][0], Context))
        self.assertDictEqual(
            context._supercontext[0][0]._config_values, supercontext._config_values
        )
        self.assertIsNone(context._supercontext[0][1])

    def test___init___supercontext_tuple(self):
        supercontext = Context({"section": {"val1": 1, "val2": 2}})

        context = Context(supercontext=(supercontext, "section"))

        self.assertTrue(isinstance(context._supercontext, list))

        self.assertTrue(isinstance(context._supercontext[0], tuple))
        self.assertTrue(isinstance(context._supercontext[0][0], Context))
        self.assertDictEqual(
            context._supercontext[0][0]._config_values, supercontext._config_values
        )
        self.assertEqual(context._supercontext[0][1], "section")

    def test_config_values(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }

        self.assertDictEqual(context._config_values, context.config_values)

    def test_config_values_super(self):
        supercontext = Context({"entry1": "super1"})

        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }
        context.supercontext = supercontext

        self.assertDictEqual(
            context.config_values,
            {
                "entry1": "super1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            },
        )

    def test_config_values_super_section(self):
        supercontext = Context({"section": {"entry1": "super1"}})

        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }
        context.supercontext = (supercontext, "section")

        self.assertDictEqual(
            context.config_values,
            {
                "entry1": "super1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            },
        )

    def test_config_values_2super(self):
        supercontexta = Context({"entry1": "supera1"})
        supercontextb = Context({"entry1": "superb1", "entry2": "superb2"})

        supercontext = [supercontexta, supercontextb]

        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }
        context.supercontext = supercontext

        self.assertDictEqual(
            context.config_values,
            {
                "entry1": "supera1",
                "entry2": "superb2",
                "entry3": "value3",
                "entry4": "value4",
            },
        )

    def test_config_values_2super_super(self):
        supersupercontext = Context({"entry1": "supersuper1"})
        supercontexta = Context({"entry1": "supera1", "entry2": "supera2"})
        supercontextb = Context(
            {"entry1": "superb1", "entry2": "superb2", "entry3": "superb3"}
        )

        supercontexta.supercontext = supersupercontext

        supercontext = [supercontexta, supercontextb]

        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
        }
        context.supercontext = supercontext

        self.assertDictEqual(
            context.config_values,
            {
                "entry1": "supersuper1",
                "entry2": "supera2",
                "entry3": "superb3",
                "entry4": "value4",
            },
        )

    def test_config_values_2super_super_2global(self):

        global_supercontexta = Context({"entry1": "globala1"})
        global_supercontextb = Context({"entry1": "globalb1", "entry2": "globalb2"})
        supersupercontext = Context(
            {"entry1": "supersuper1", "entry2": "supersuper2", "entry3": "supersuper3"}
        )
        supercontexta = Context(
            {
                "entry1": "supera1",
                "entry2": "supera2",
                "entry3": "supera3",
                "entry4": "supera4",
            }
        )
        supercontextb = Context(
            {
                "entry1": "superb1",
                "entry2": "superb2",
                "entry3": "superb3",
                "entry4": "superb4",
                "entry5": "superb5",
            }
        )

        supercontexta.supercontext = supersupercontext

        supercontext = [supercontexta, supercontextb]

        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": "value2",
            "entry3": "value3",
            "entry4": "value4",
            "entry5": "value5",
            "entry6": "value6",
        }
        context.supercontext = supercontext

        with patch(
            "processor_tools.context.GLOBAL_SUPERCONTEXT",
            [(global_supercontexta, None), (global_supercontextb, None)],
        ) as m:
            self.assertDictEqual(
                context.config_values,
                {
                    "entry1": "globala1",
                    "entry2": "globalb2",
                    "entry3": "supersuper3",
                    "entry4": "supera4",
                    "entry5": "superb5",
                    "entry6": "value6",
                },
            )

    def test_update(self):
        context = Context()
        context._config_values = {
            "entry1": "value1",
            "entry2": {"subentry2a": "value2a", "subentry2b": "value2b"}
        }

        context.update({"entry2": {"subentry2a": "update"}})

        self.assertDictEqual(
            context._config_values,
            {
                "entry1": "value1",
                "entry2": {"subentry2a": "update", "subentry2b": "value2b"}
            }
        )

    @patch(
        "processor_tools.context.Context.config_values",
        new_callable=PropertyMock(
            return_value={
                "entry1": "value1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            }
        ),
    )
    def test_get_config_names(self, mock_config):
        context = Context()

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

    @patch(
        "processor_tools.context.Context.config_values",
        new_callable=PropertyMock(
            return_value={
                "entry1": "value1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            }
        ),
    )
    def test_get(self, mock_config_values):
        context = Context()
        self.assertEqual(context.get("entry2"), "value2")

    @patch(
        "processor_tools.context.Context.config_values",
        new_callable=PropertyMock(
            return_value={
                "entry1": "value1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            }
        ),
    )
    def test_get_missing(self, mock_config_values):
        context = Context()
        self.assertIsNone(context.get("entry5"))

    @patch(
        "processor_tools.context.Context.config_values",
        new_callable=PropertyMock(
            return_value={
                "entry1": "value1",
                "entry2": "value2",
                "entry3": "value3",
                "entry4": "value4",
            }
        ),
    )
    def test_get_missing_with_default(self, mock_config_values):
        context = Context()
        self.assertEqual(context.get("entry5", "hello"), "hello")

    @patch(
        "processor_tools.context.Context.config_values",
        new_callable=PropertyMock(
            return_value={
                "entry1": "value1",
                "entry2": {"subentry2a": "value2a"},
                "entry3": "value3",
                "entry4": "value4",
            }
        ),
    )
    def test_get_sub(self, mock_config_values):
        context = Context()
        self.assertDictEqual(context.get("entry2"), {"subentry2a": "value2a"})

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
    def tearDown(self):

        clear_global_supercontext()

    def test_function_call(self):

        context = Context({"val": 1})
        set_global_supercontext(context)

        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
        self.assertDictEqual(
            GLOBAL_SUPERCONTEXT[0][0]._config_values, context._config_values
        )
        self.assertIsNone(GLOBAL_SUPERCONTEXT[0][1])

    def test_function_call_section(self):

        print(GLOBAL_SUPERCONTEXT)

        context = Context({"val": 1})
        set_global_supercontext((context, "section"))

        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
        self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
        self.assertDictEqual(
            GLOBAL_SUPERCONTEXT[0][0]._config_values, context._config_values
        )
        self.assertEqual(GLOBAL_SUPERCONTEXT[0][1], "section")
        clear_global_supercontext()

    def test_function_call_invalid(self):

        self.assertRaises(TypeError, set_global_supercontext, "hello")

    def test_with(self):

        context = Context({"val": 1})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)
        with set_global_supercontext(context):

            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
            self.assertDictEqual(
                GLOBAL_SUPERCONTEXT[0][0]._config_values, context._config_values
            )
            self.assertIsNone(GLOBAL_SUPERCONTEXT[0][1])

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)

    def test_with_nested(self):

        context1 = Context({"val1": 1})
        context2 = Context({"val2": 2})

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)
        with set_global_supercontext(context1):
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
            self.assertDictEqual(
                GLOBAL_SUPERCONTEXT[0][0]._config_values, context1._config_values
            )
            self.assertIsNone(GLOBAL_SUPERCONTEXT[0][1])

            with set_global_supercontext(context2):

                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
                self.assertEqual(len(GLOBAL_SUPERCONTEXT), 2)

                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
                self.assertDictEqual(
                    GLOBAL_SUPERCONTEXT[0][0]._config_values, context1._config_values
                )
                self.assertIsNone(GLOBAL_SUPERCONTEXT[0][1])

                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[1], tuple))
                self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[1][0], Context))
                self.assertDictEqual(
                    GLOBAL_SUPERCONTEXT[1][0]._config_values, context2._config_values
                )
                self.assertIsNone(GLOBAL_SUPERCONTEXT[1][1])

            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT, list))
            self.assertEqual(len(GLOBAL_SUPERCONTEXT), 1)
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0], tuple))
            self.assertTrue(isinstance(GLOBAL_SUPERCONTEXT[0][0], Context))
            self.assertDictEqual(
                GLOBAL_SUPERCONTEXT[0][0]._config_values, context1._config_values
            )
            self.assertIsNone(GLOBAL_SUPERCONTEXT[0][1])

        self.assertEqual(len(GLOBAL_SUPERCONTEXT), 0)


if __name__ == "__main__":
    unittest.main()
