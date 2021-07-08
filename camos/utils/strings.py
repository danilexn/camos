# -*- coding: utf-8 -*-
# Created on Tue Jul 06 2021
# Last modified on Tue Jul 06 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

# Taken from StackOverflow
# /58625817/pythonic-way-to-change-range-expression-into-a-list
def dashrange(s):
    """Parses individual groups of ranges inside an already
    (comma)-separated list, e.g, ["0-4","12"]. It returns a flat
    list with all numbers between the range

    Args:
        s (str): string containing dashes

    Returns:
        list: list of integers between the range
    """
    if "-" in s:
        a, b = map(int, s.split("-"))
        return range(a, b + 1)
    return [int(s)]


# Taken from StackOverflow
# /58625817/pythonic-way-to-change-range-expression-into-a-list
def range_to_list(s):
    """Retrieves a comma-separated string, splits it into
    the individual elements, which may contain dashes,
    then puts those into the dashrange method to retrieve
    ranges. Returns the flat list containing the desired numbers
    Example: "0-5,10" will return [0, 1, 2, 3, 4, 5, 10]

    Args:
        s (string): comma separated list of numbers and dashes (ranges)

    Returns:
        list[int]: generated list of integers
    """
    return [j for i in s.split(",") for j in dashrange(i)]
