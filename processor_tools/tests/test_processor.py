"""processor_tools.tests.test_processor - tests for processor_tools.test_processor"""

import shutil
import unittest
from unittest.mock import patch, call, MagicMock
import string
import random
import os
from processor_tools.processor import BaseProcessor
from processor_tools.processor import ProcessorFactory


__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


THIS_DIRECTORY = os.path.dirname(__file__)


class TestBaseProcessor(unittest.TestCase):
    def setUp(self) -> None:
        class TestProcessor(BaseProcessor):
            pass

        class Option1(BaseProcessor):
            pass

        class Option2(BaseProcessor):
            pass

        test_factory = ProcessorFactory()
        test_factory["option1"] = Option1
        test_factory["option2"] = Option2

        self.TestProcessor = TestProcessor
        self.test_processor = self.TestProcessor()
        self.test_factory = test_factory

    def test___init___None(self):
        p = BaseProcessor()

        self.assertEqual(type(p.context), dict)

    def test___init___context(self):
        p = BaseProcessor("a")

        self.assertEqual(p.context, "a")

    @patch("processor_tools.processor.BaseProcessor.append_subprocessor")
    def test___init___cls_subprocessor(self, mock_append):
        class TestProcessor(BaseProcessor):
            cls_subprocessors = {"sp1": "a", "sp2": "b"}

        p = TestProcessor()

        mock_append.assert_has_calls([call("sp1", "a"), call("sp2", "b")])

    def test_processor_name_set__name(self):

        p = self.TestProcessor()
        p.cls_processor_name = "test"
        self.assertEqual(p.processor_name, "test")

    def test_processor_name_unset__name(self):
        p = self.TestProcessor()
        self.assertEqual(p.processor_name, "TestProcessor")

    def test_append_subprocessor_obj(self):

        test_processor = self.TestProcessor()
        test_subprocessor = self.TestProcessor()

        test_processor.append_subprocessor("subprocessor", test_subprocessor)

        self.assertCountEqual(test_processor.subprocessors.keys(), ["subprocessor"])
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_name, "TestProcessor"
        )
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_path, "subprocessor"
        )

    def test_append_subprocessor_cls(self):

        test_processor = self.TestProcessor()

        test_processor.append_subprocessor("subprocessor", self.TestProcessor)

        self.assertCountEqual(test_processor.subprocessors.keys(), ["subprocessor"])
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_name, "TestProcessor"
        )
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_path, "subprocessor"
        )

    def test_append_subprocessor_factory(self):

        test_processor = self.TestProcessor(context={"subprocessor": "option1"})

        test_processor.append_subprocessor("subprocessor", self.test_factory)

        self.assertCountEqual(test_processor.subprocessors.keys(), ["subprocessor"])
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_name, "Option1"
        )
        self.assertEqual(
            test_processor.subprocessors["subprocessor"].processor_path, "subprocessor"
        )

    def test_run_1arg(self):
        test_processor = self.TestProcessor()

        processor1 = MagicMock()
        processor1.run.return_value = "p1"

        processor2 = MagicMock()
        processor2.run.return_value = "p2"

        test_processor.subprocessors = {
            "processor1": processor1,
            "processor2": processor2,
        }

        val = test_processor.run("p0")

        processor1.run.assert_called_once_with("p0")
        processor2.run.assert_called_once_with("p1")
        self.assertEqual("p2", val)

    def test_run_2arg(self):
        test_processor = self.TestProcessor()

        processor1 = MagicMock()
        processor1.run.return_value = ("p1a", "p1b")

        processor2 = MagicMock()
        processor2.run.return_value = ("p2a", "p2b")

        test_processor.subprocessors = {
            "processor1": processor1,
            "processor2": processor2,
        }

        val = test_processor.run("p0a", "p0b")

        processor1.run.assert_called_once_with("p0a", "p0b")
        processor2.run.assert_called_once_with("p1a", "p1b")
        self.assertEqual(("p2a", "p2b"), val)


class TestBaseProcessorFactory(unittest.TestCase):
    def setUp(self) -> None:

        # Create temporary module
        letters = string.ascii_lowercase
        self.tmp_mod = "tmp_" + "".join(random.choice(letters) for i in range(5))
        self.tmp_mod_dir = os.path.join(THIS_DIRECTORY, self.tmp_mod)
        os.makedirs(self.tmp_mod_dir)

        mod1 = """
from processor_tools.processor import BaseProcessor
class Test1:
    pass

class Test2(BaseProcessor):
    pass
    """

        with open(os.path.join(self.tmp_mod_dir, "mod1.py"), "w") as f:
            f.write(mod1)

        mod2 = """
from processor_tools.processor import BaseProcessor
class Test3:
    pass

class Test4(BaseProcessor):
    pass
    """

        with open(os.path.join(self.tmp_mod_dir, "mod2.py"), "w") as f:
            f.write(mod2)

        self.mod1_name = ".".join(["processor_tools", "tests", self.tmp_mod, "mod1"])
        self.mod2_name = ".".join(["processor_tools", "tests", self.tmp_mod, "mod2"])

        self.test_factory = ProcessorFactory([self.mod1_name, self.mod2_name])

    def test__find_processors_1mod(self):
        classes = self.test_factory._find_processors(self.mod1_name)
        self.assertCountEqual(classes.keys(), ["Test2"])

    def test__find_processors_2mod(self):
        classes = self.test_factory._find_processors([self.mod1_name, self.mod2_name])
        self.assertCountEqual(classes.keys(), ["Test2", "Test4"])

    def test_keys(self):
        self.assertEqual(self.test_factory.keys(), ["Test2", "Test4"])

    def test___setitem__(self):
        class Test5(BaseProcessor):
            pass

        test_factory = ProcessorFactory()
        test_factory["test"] = Test5
        self.assertTrue(("test" in test_factory._processors))

    def test__delitem__(self):

        test_factory = ProcessorFactory(self.mod1_name)
        del test_factory["Test2"]
        self.assertTrue(("Test2" not in test_factory._processors))

    def test___getitem__(self):
        self.assertEqual(self.test_factory["Test2"].__name__, "Test2")

    def tearDown(self):
        shutil.rmtree(self.tmp_mod_dir)


if __name__ == "__main__":
    unittest.main()
