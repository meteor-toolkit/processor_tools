"""processor_tools.tests.test_processor - tests for processor_tools.test_processor"""

import unittest
from processor_tools.processor import BaseProcessor

__author__ = "Sam Hunt <sam.hunt@npl.co.uk>"
__all__ = []


class TestBaseProcessor(unittest.TestCase):
    def test___init___None(self):
        p = BaseProcessor()

        self.assertEqual(type(p.context), dict)

    def test___init__(self):
        p = BaseProcessor("a")

        self.assertEqual(p.context, "a")


if __name__ == "__main__":
    unittest.main()
