"""processor_tools.utils.tests.test_formatters - test for processor_tools.utils.formatters"""

import datetime as dt
import numpy as np
import unittest
import unittest.mock as mock
import datetime as dt
from processor_tools.utils.formatters import *

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"

__all__ = []


class TestFormatters(unittest.TestCase):
    def test_is_number_int(self):
        self.assertTrue(is_number("9"))

    def test_is_number_float(self):
        self.assertTrue(is_number("4.3"))

    def test_is_number_negative_float(self):
        self.assertTrue(is_number("-0.5"))

    def test_is_number_letter(self):
        self.assertFalse(is_number("l"))

    def test_is_datetime_microseconds(self):
        self.assertTrue(is_datetime("2022-09-10T20:23:47.111356Z"))
        self.assertTrue(is_datetime("2022-09-10T20:23:47.111356"))

    def test_is_datetime_seconds(self):
        self.assertTrue(is_datetime("2022-09-10T20:23:47Z"))
        self.assertTrue(is_datetime("2022-09-10T20:23:47"))

    def test_is_datetime_int(self):
        self.assertFalse(is_datetime("23451232"))

    def test_str2datetime_microseconds(self):
        self.assertEqual(
            str2datetime("2022-09-10T20:23:47.111356Z"),
            dt.datetime(2022, 9, 10, 20, 23, 47, 111356),
        )
        self.assertEqual(
            str2datetime("2022-09-10T20:23:47.111356"),
            dt.datetime(2022, 9, 10, 20, 23, 47, 111356),
        )

    def test_str2datetime_seconds(self):
        self.assertEqual(
            str2datetime("2022-09-10T20:23:47Z"), dt.datetime(2022, 9, 10, 20, 23, 47)
        )
        self.assertEqual(
            str2datetime("2022-09-10T20:23:47"), dt.datetime(2022, 9, 10, 20, 23, 47)
        )

    def test_str2datetime_date(self):
        self.assertEqual(str2datetime("2022-09-10"), dt.datetime(2022, 9, 10, 0, 0))

    def test_str2datetime_time(self):
        self.assertEqual(str2datetime("20:23:47"), dt.time(20, 23, 47))
        self.assertEqual(str2datetime("20:23:47.111356Z"), dt.time(20, 23, 47, 111356))
        self.assertEqual(
            str2datetime("20:23:47.11135654Z"), dt.time(20, 23, 47, 111356)
        )

    def test_val_format_str(self):
        self.assertEqual(val_format("str"), "str")
        self.assertEqual(
            val_format("multiple separated strings"), "multiple separated strings"
        )
        self.assertEqual(
            val_format("this=text;that=text;other=text"),
            {"this": "text", "that": "text", "other": "text"},
        )
        self.assertEqual(
            val_format("this=text;that=text;and the other=text"),
            {"this": "text", "that": "text", "and the other": "text"},
        )

    def test_val_format_int(self):
        self.assertEqual(val_format("2"), 2)
        self.assertEqual(val_format("1 2 3 4 5"), [1, 2, 3, 4, 5])

    def test_val_format_float(self):
        self.assertEqual(val_format("2.3"), 2.3)
        self.assertEqual(val_format("1.2 1.3 1.4 1.5"), [1.2, 1.3, 1.4, 1.5])
        self.assertEqual(val_format("0.8 1 1.2"), [0.8, 1.0, 1.2])

    def test_val_format_other(self):
        self.assertEqual(val_format({"A": "a"}), {"A": "a"})

    # todo - look into nested dictionaries
    def test_list_to_dict(self):
        input_list = [
            ("GROUP", "Satellite"),
            ("Name", "Sentinel 2A"),
            ("Agency", "European Space Agency"),
            ("Launch_Date", "23 June 2015"),
            ("END_GROUP", "Satellite"),
            ("GROUP", "Metadata"),
            ("Aquisition_time", "01:51:58"),
            ("Processing_time", "03:21:37"),
            ("END_GROUP", "Metadata"),
            ("GROUP", "BAND_1"),
            ("Name", "Spectral band 1"),
            ("END_GROUP", "BAND_1"),
        ]
        output_dict = {
            "Satellite": {
                "Name": "Sentinel 2A",
                "Agency": "European Space Agency",
                "Launch_Date": "23 June 2015",
            },
            "Metadata": {
                "Aquisition_time": "01:51:58",
                "Processing_time": "03:21:37",
            },
            "BAND_1": {
                "Name": "Spectral band 1",
            },
        }

        self.maxDiff = None
        self.assertDictEqual(list_to_dict(input_list), output_dict)

    def test_txt_to_dict(self):
        pass

    def test_datetime_from_yearday(self):
        test_date = datetime_from_yearday(2022, 100, "08:30:46")
        assert test_date == dt.datetime(2022, 4, 10, 8, 30)

        test_date = datetime_from_yearday(2020, 180, 1300.0)
        assert test_date == dt.datetime(2020, 6, 28, 13, 0)

        test_date = datetime_from_yearday(2020, 180, "1300")
        assert test_date == dt.datetime(2020, 6, 28, 13, 0)

    def test_convert_datetime(self):
        date = np.datetime64("2022-06-15T10:30:00")
        combined = convert_datetime(date)
        assert combined == dt.datetime(2022, 6, 15, 10, 30, tzinfo=dt.timezone.utc)

        # test various string formats
        date_str = "2022-06-15"
        combined_str = convert_datetime(date_str)
        assert combined_str == dt.datetime(2022, 6, 15, tzinfo=dt.timezone.utc)

        date_str_time = "2022-06-15T10:30:00Z"
        combined_str_time = convert_datetime(date_str_time)
        assert combined_str_time == dt.datetime(
            2022, 6, 15, 10, 30, tzinfo=dt.timezone.utc
        )

        # test various numpy formats
        date_np = np.datetime64("2022-06-15T10:30:00+10:00")
        combined_np = convert_datetime(date_np)
        assert combined_np == dt.datetime(2022, 6, 15, 00, 30, tzinfo=dt.timezone.utc)

        # test float/int formats
        date_int = np.datetime64(1655251800, "s")
        combined_int = convert_datetime(date_int)
        assert combined_int == dt.datetime(2022, 6, 15, 00, 10, tzinfo=dt.timezone.utc)

        date_float = 1655251800.5
        combined_float = convert_datetime(date_float)
        assert combined_float == dt.datetime(
            2022, 6, 15, 0, 10, 0, 500000, tzinfo=dt.timezone.utc
        )


if __name__ == "__main__":
    unittest.main()
