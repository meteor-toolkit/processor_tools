"""processor_tools.tests.test_processor_builder - tests for processor_tools.test_processor_builder"""

import shutil
import unittest
import string
import random
import os
from processor_tools.processor import BaseProcessor
from processor_tools.processor_builder import BaseProcessorFactory

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


this_directory = os.path.dirname(__file__)


class TestBaseProcessorFactory(unittest.TestCase):
    def setUp(self) -> None:

        # Create temporary module
        letters = string.ascii_lowercase
        self.tmp_mod = "tmp_" + "".join(random.choice(letters) for i in range(5))
        self.tmp_mod_dir = os.path.join(this_directory, self.tmp_mod)
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

        class TestFactory(BaseProcessorFactory):
            _module_name = [self.mod1_name, self.mod2_name]

        self.TestFactory = TestFactory
        self.test_factory = TestFactory()

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

        test_factory = self.TestFactory()
        test_factory["test"] = Test5
        self.assertTrue(("test" in test_factory._processors))

    def test__delitem__(self):

        test_factory = self.TestFactory()
        del test_factory["Test2"]
        self.assertTrue(("Test2" not in test_factory._processors))

    def test___getitem__(self):
        self.assertEqual(self.test_factory["Test2"].__name__, "Test2")

    def tearDown(self):
        shutil.rmtree(self.tmp_mod_dir)


if __name__ == "__main__":
    unittest.main()
