#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: provider.py
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

"""Provide payload data for Internet Control Message Protocol (ICMP), with no header."""


class PayloadProviderBase:
    def __init__(self):
        raise NotImplementedError('Cannot create instances of PayloadProviderBase')

    def __iter__(self):
        """Implement iter(self)."""

        raise NotImplementedError()

    def __next__(self):
        """Implement next(self)."""

        raise NotImplementedError()


class List(PayloadProviderBase):
    def __init__(self, payload_list):
        """Creates a provider of payloads from an existing list of payloads."""

        self.__payloads = payload_list
        self.__counter = 0

    def __iter__(self):
        """Implement iter(self)."""

        self.__counter = 0

        return self

    def __next__(self):
        """Implement next(self)."""

        if self.__counter < len(self.__payloads):
            ret = self.__payloads[self.__counter]
            self.__counter += 1
            return ret

        raise StopIteration


class Repeat(PayloadProviderBase):
    def __init__(self, pattern, count):
        """Creates a provider of many identical payloads."""

        self.pattern = pattern
        self.count = count
        self.__counter = 0

    def __iter__(self):
        """Implement iter(self)."""

        self.__counter = 0

        return self

    def __next__(self):
        """Implement next(self)."""

        if self.__counter < self.count:
            self.__counter += 1

            return self.pattern

        raise StopIteration


class Sweep(PayloadProviderBase):
    def __init__(self, pattern, start_size, end_size):
        """Creates a provider of payloads of increasing size."""

        if start_size > end_size:
            raise ValueError('end_size must be greater or equal than start_size')

        if len(pattern) == 0:
            raise ValueError('pattern cannot be empty')

        self.pattern = pattern
        self.start_size = start_size
        self.end_size = end_size

        # Extend the length of the pattern if needed
        while not len(self.pattern) >= end_size:
            self.pattern += pattern

        self.__current_size = self.start_size

    def __iter__(self):
        """Implement iter(self)."""

        self.__current_size = self.start_size

        return self

    def __next__(self):
        """Implement next(self)."""

        if self.__current_size <= self.end_size:
            ret = self.pattern[0:self.__current_size]
            self.__current_size += 1

            return ret

        raise StopIteration
