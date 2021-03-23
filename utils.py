#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: utils.py
#  Version: 0.0.1
#  Summary: Marvin a Pinpoint Network Problems
#           Visualize network performance data across hundreds of targets with tools built for monitoring both
#           local and remote devices, helping you find and fix problems fast.
#
#  Author: Alexsander Lopes Camargos
#  Author-email: alcamargos@vivaldi.net
#
#  License: MIT
#
#  --------------------------------------------------------------------------------------------------------------------

"""Some useful classes and functions for code reuse."""

import enum

from random import choice
from string import printable as printable_character


class SuccessRequest(enum.IntEnum):
    # Automatically assign the integer value to the values of enum class attributes.
    one = enum.auto()
    most = enum.auto()
    all = enum.auto()


class SeedIds:
    def __init__(self, ids=None):
        # Preventing the default argument value of ids is changeable.
        if ids is None:
            ids = []

        self.__ids = ids

    @property
    def ids(self):
        return self.__ids


class ICMPData(enum.Enum):
    # Default ICMPPacket header.
    ICMP_STRUCTURE_FMT = 'bbHHh'
    # Ethernet, IP and ICMPPacket header lengths combined
    LEN_TO_PAYLOAD = 41


def random_text(size):
    """Returns a random text of the specified size."""

    return ''.join(choice(printable_character) for _ in range(size))


def represent_seconds_in_milliseconds(seconds):
    """Converts seconds into human-readable milliseconds with 2 digits decimal precision"""

    return round(seconds * 1000, 2)
