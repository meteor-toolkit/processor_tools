"""processor_tools.utils.tests.test_dict_tools - test for processor_tools.utils.dict_tools"""

import unittest
import unittest.mock as mock

from processor_tools.utils.dict_tools import *


class MyDictTools(unittest.TestCase):
    @mock.patch("processor_tools.utils.dict_tools.get_value_gen", autospec=False)
    def test_get_value_multiple_values(self, mm):
        input_1 = {
            "Labs": {
                "Ground_Floor": [{"Science": "G1", "Art": []}],
                "First_Floor": [{"Science": "F1", "Art": []}],
            }
        }
        output_1 = [("Science", "G1"), ("Science", "F1")]

        def fake(input, key):
            yield from output_1

        mm.side_effect = fake
        self.assertEqual(get_value(input_1, "Science"), output_1)

    @mock.patch("processor_tools.utils.dict_tools.get_value_gen", autospec=True)
    def test_get_value_multiple_levels(self, mm):
        input_1 = {
            "Main_Building": {
                "Rooms": {"Ground_Floor": "A1"},
                "Labs": {"Ground_Floor": "L1"},
            },
            "Sports_Hall": {"Ground_Floor": "Changing_Rooms"},
        }
        output_1 = [
            ("Ground_Floor", "A1"),
            ("Ground_Floor", "L1"),
            ("Ground_Floor", "Changing_Rooms"),
        ]

        def fake(input, key):
            yield from output_1

        mm.side_effect = fake
        self.assertEqual(get_value(input_1, "Ground_Floor"), output_1)

    @mock.patch("processor_tools.utils.dict_tools.get_value_gen", autospec=True)
    def test_get_value_single_value(self, mm):
        input_1 = {"Main_Building": {"Labs": {"Ground_Floor": "L1"}}}
        output_1 = {"Ground_Floor": "L1"}
        iter_obj = [("Labs", output_1)]

        def fake(input, key):
            yield from iter_obj

        mm.side_effect = fake
        self.assertEqual(get_value(input_1, "Labs"), output_1)

    @mock.patch("processor_tools.utils.dict_tools.get_value_gen", autospec=True)
    def test_get_value_duplicate_value(self, mm):
        input_1 = {"Main_Building": {"Height": "5 m"}, "Sports_Hall": {"Height": "5 m"}}
        output_1 = "5 m"
        iter_obj = [("Height", "5 m"), ("Height", "5 m")]

        def fake(input, key):
            yield from iter_obj

        mm.side_effect = fake
        self.assertEqual(get_value(input_1, "Height"), output_1)

    @mock.patch("processor_tools.utils.dict_tools.get_value_gen", autospec=True)
    def test_get_value_nonexistent_key(self, mm):
        input_1 = {"Main_Building": {"Labs": {"Ground_Floor": "L1"}}}

        def fake(input, key):
            yield from []

        mm.side_effect = fake
        self.assertEqual(get_value(input_1, "Storage"), None)


    def test_get_value_gen(self):
        input_1 = {"Rooms": {"Ground_Floor": "A1"}}
        output_1 = [("Ground_Floor", "A1")]

        self.assertEqual(list(get_value_gen(input_1, "Ground_Floor")), output_1)

        input_2 = {"Rooms": {"Ground_Floor": "A1"}, "Labs": {"Ground_Floor": "L1"}}
        output_2 = [("Ground_Floor", "A1"), ("Ground_Floor", "L1")]

        self.assertEqual(list(get_value_gen(input_2, "Ground_Floor")), output_2)

        input_3 = {
            "Building": {
                "Rooms": {"Ground_Floor": "A1"},
                "Labs": {"Ground_Floor": "L1"},
            }
        }
        output_3 = [("Ground_Floor", "A1"), ("Ground_Floor", "L1")]

        self.assertEqual(list(get_value_gen(input_3, "Ground_Floor")), output_3)

        input_4 = {
            "Main_Building": {
                "Rooms": {"Ground_Floor": "A1"},
                "Labs": {"Ground_Floor": "L1"},
            },
            "Sports_Hall": {"Ground_Floor": "Changing_Rooms"},
        }
        output_4 = [
            ("Ground_Floor", "A1"),
            ("Ground_Floor", "L1"),
            ("Ground_Floor", "Changing_Rooms"),
        ]

        self.assertEqual(list(get_value_gen(input_4, "Ground_Floor")), output_4)

        input_5 = {
            "Labs": {
                "Ground_Floor": [{"Science": "G1", "Art": []}],
                "First_Floor": [{"Science": "F1", "Art": []}],
            }
        }
        output_5 = [("Science", "G1"), ("Science", "F1")]

        self.assertEqual(list(get_value_gen(input_5, "Science")), output_5)

        input_6 = {
            "Labs": {
                "Ground_Floor": [{"Science": "G1", "Art": []}],
                "First_Floor": [{"Science": "F1", "Art": []}],
            },
            "Subjects": {"Science": "Triple"},
        }
        output_6 = [("Science", "G1"), ("Science", "F1"), ("Science", "Triple")]

        self.assertEqual(list(get_value_gen(input_6, "Science")), output_6)


if __name__ == "__main__":
    unittest.main()
