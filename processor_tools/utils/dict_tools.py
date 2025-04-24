"""processor_tools.utils.dict_tools - dictionary utility functions"""

from copy import copy, deepcopy
from typing import Any, Dict, Generator, List, Optional, Union

import numpy as np


__author__ = "Mattea Goalen <mattea.goalen@npl.co.uk>"

__all__ = [
    "get_value",
    "get_value_gen",
]


def get_value_gen(test_dict: dict, key: str) -> Generator:
    """
    Get generator function of dictionary values associated with the specified key

    :param test_dict: input iterator in which to search for the key-values pair/s
    :param key: key to use to search through dictionary
    :return: generator function containing key-value pair/s
    """
    if isinstance(test_dict, dict):
        for k, v in zip(list(test_dict.keys()), list(test_dict.values())):
            if k == key:
                t = deepcopy(test_dict.get(k))
                yield k, t
            elif isinstance(v, list) and all([isinstance(i, dict) for i in v]):
                for i, vel in enumerate(v):
                    yield from get_value_gen(test_dict[k][i], key)
            else:
                yield from (
                    [] if not isinstance(v, dict) else get_value_gen(test_dict[k], key)
                )
    elif isinstance(test_dict, list) and all([isinstance(i, dict) for i in test_dict]):
        for i, vel in enumerate(test_dict):
            yield from get_value_gen(test_dict[i], key)


def get_value(test_dict, key, multiple=False):
    """
    Return dictionary values associated with the specified key

    :param multiple:
    :param test_dict: input dictionary in which to search for the key-value pair/s
    :param key: key to use to search through dictionary
    :return: list of multiple values or single value associated with key
    """
    value_list = list(get_value_gen(test_dict, key))
    try:
        if len(value_list) == 1 or all(
            [True if i[1] == value_list[0][1] else False for i in value_list]
        ):
            if multiple:
                return value_list
            else:
                return dict(value_list)[key]
    except KeyError:
        return None
    except ValueError:
        pass
    if multiple is True and value_list:
        return value_list
    elif value_list:
        print(
            "Multiple different values found to be associated with '{}'. Consider filtering dictionary further.".format(
                key
            )
        )
        return value_list
    print(
        "No value found associated with '{}'. Check spelling and letter case.".format(
            key
        )
    )
    return


if __name__ == '__main__':
    pass