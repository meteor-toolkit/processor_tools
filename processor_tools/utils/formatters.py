"""processor_tools.utils.formatters - formatting functions for values"""

import datetime as dt
import numpy as np
from dateutil.parser import parse  # type: ignore[import-untyped]
from typing import Union

__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"

__all__ = [
    "is_number",
    "is_datetime",
    "str2datetime",
    "val_format",
    "list_to_dict",
    "txt_to_dict",
    "convert_datetime",
]


def is_number(s):
    """
    Return whether a string is a number

    :param s: input str
    :return: bool
    """
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def is_datetime(s):
    """
    Return whether a string is a datetime

    :param s: input string
    :return: bool
    """
    try:
        parse(s, fuzzy=False)
    except ValueError:
        return False
    else:
        return True


def str2datetime(s):
    """
    Convert strings of recognised datetime formats (valid ISO 8601 formats accepted by
    datetime.datetime.fromisoformat() and datetime.time.fromisoformat()) to datetime objects.

    Valid date strings given by:
    datetime.datetime.fromisoformat() - https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
    datetime.time.isoformat() - https://docs.python.org/3/library/datetime.html#datetime.time.fromisoformat

    :param s: input string
    :return: datetime object or original string value
    """
    if s[-1] == "Z":
        s = s[:-1]
    try:
        val = dt.datetime.fromisoformat(s)
    except ValueError:
        try:
            val = dt.datetime.fromisoformat(s[:26])
        except ValueError:
            try:
                val = dt.time.fromisoformat(s[:15])
            except ValueError:
                try:
                    val = parse(s, fuzzy=False)
                except ValueError:
                    raise ValueError(
                        "Unable to discern datetime requested: '{}'".format(s)
                    )
    return val

def convert_datetime(
    date_time: Union[dt.datetime, dt.date, str, float, int, np.ndarray],
) -> dt.datetime:
    """
    Convert input datetimes to a datetime object

    :param date_time: date time to convert to a datetime object
    :return: datetime object corresponding to input date_time
    """
    if isinstance(date_time, np.ndarray):
        date_time_out = np.array([convert_datetime(date_time_i) for date_time_i in date_time])
    elif isinstance(date_time, dt.datetime):
        date_time_out = date_time
    elif isinstance(date_time, dt.date):
        date_time_out = dt.datetime.combine(date_time, dt.time())
    elif isinstance(date_time, np.datetime64):
        unix_epoch = np.datetime64(0, "s")
        one_second = np.timedelta64(1, "s")
        seconds_since_epoch = (date_time - unix_epoch) / one_second
        date_time_out = dt.datetime.fromtimestamp(seconds_since_epoch,tz=dt.timezone.utc)
    elif isinstance(date_time, (float, int, np.unsignedinteger, np.floating)):
        date_time_out = dt.datetime.fromtimestamp(float(date_time),tz=dt.timezone.utc)
    elif isinstance(date_time, str):
        date_time_out = str2datetime(date_time).replace(tzinfo=dt.timezone.utc)
    else:
        raise ValueError(
            "Unable to discern datetime '{}' of type: '{}'".format(date_time, type(date_time))
        )
    if isinstance(date_time_out, np.ndarray):
        for i in range(len(date_time_out)):
            if date_time_out[i].tzinfo is None:
                date_time_out[i] = date_time_out[i].replace(tzinfo=dt.timezone.utc)
    elif date_time_out.tzinfo is None:
        date_time_out = date_time_out.replace(tzinfo=dt.timezone.utc)

    return date_time_out

def datetime_from_yearday(year, doy, utc):
    """
    """

    if isinstance(utc, str):
        if ':' in utc:
            utc = utc.replace(":", "")
        try:
            utc = dt.datetime.strptime(utc, "%H%M")
        except ValueError:
            import warnings
            warnings.warn(f"seconds provided {utc} - slicing to hours/minutes f{utc[0:4]}")
            utc = dt.datetime.strptime(utc[0:4], "%H%M")

    elif isinstance(utc, float):  # if the time is float we must convert to string and remove the ".0"
        utc = dt.datetime.strptime(str(utc).split(".")[0], "%H%M")
    doyDelta = dt.timedelta(days=int(doy) - 1)

    return dt.datetime(int(year), 1, 1, utc.hour, utc.minute) + doyDelta

def val_format(s):
    """
    Change recognised formats of input strings into different types

    :param s: input value
    :return: newly formatted string (or original input value)
    """
    if type(s) is str:
        v = s.split(";")
        if len(v) == 1:
            v = v[0].split(" ")
        if len(v) == 1:
            try:
                val = int(v[0])
            except ValueError:
                if is_number(v[0]):
                    val = float(v[0])
                elif is_datetime(v[0]):
                    val = str2datetime(v[0])
                else:
                    val = v[0]
        else:
            val = [0] * len(v)
            for i, vi in enumerate(v):
                try:
                    val[i] = int(v[i])
                except ValueError:
                    if is_number(vi):
                        val[i] = float(vi)
                    elif is_datetime(vi):
                        val[i] = str2datetime(vi)
                    else:
                        val[i] = vi
            if all([type(j) for j in val]) is True and type(val[0]) is str:
                if "=" not in val[0]:
                    val = " ".join(
                        [str(k) for k in val]
                    )  # if all values are string and not key_value pairs .join()
                else:
                    val = {}
                    for vi in v:
                        k, vv = vi.split("=")
                        val[k] = val_format(vv)
            elif (
                any([type(j) is str for j in val]) is False
                and any([type(j) is dt.datetime for j in val]) is False
                and all([type(j) for j in val]) is False
            ):
                val = [float(j) for j in val]
    else:
        val = s
    return val


# todo - look into nested dictionaries
def list_to_dict(test_list, key=None) -> dict:
    """
    Convert a list of tuples into a dictionary, based on 'GROUP' and 'END_GROUP' values

    :param test_list: list of tuples containing (key, value), ("GROUP", key) and ("END_GROUP", key) tuples
    :param key: key of the dictionary into which subsequent key-value pairs are added
    :return d: dictionary containing test_list key-value pairs
    """
    d: dict = {}
    for i, e in enumerate(test_list):
        if e[0] == "GROUP":
            key = e[1]
            values = [list(j.keys()) for k, j in enumerate(list(d.values())) if k == 0]
            if len(values) == 0 or key not in values[0]:
                d[key] = list_to_dict(test_list[i + 1 :], key)
            key = None
        elif e[0] == "END_GROUP" and e[1] == key:
            return d
        elif key is not None:
            d.update({e[0]: e[1]})
        else:
            pass
    return d


def txt_to_dict(txt_filepath):
    """
    Read in text file into a dictionary

    :param txt_filepath: text file filepath from which to read
    """
    with open(txt_filepath) as mtl:
        lines = mtl.readlines()

    elements = [
        (j[0].strip().strip('""'), j[1].strip().strip('""'))
        for j in [i.strip().split("\n")[0].split("=") for i in lines]
        if len(j) == 2
    ]

    return list_to_dict(elements)


if __name__ == "__main__":
    pass
