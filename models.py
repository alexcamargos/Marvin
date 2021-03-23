#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: models.py
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

"""A base Internet Control Message Protocol - ICMPPacket packet (RFC 792)."""

import os
import struct

from utils import ICMPData


class ICMPBaseType:
    """Represents an ICMPPacket type, as combination of type and code.

    ICMPPacket Types should inherit from this class so that the code can identify them easily."""

    def __init__(self):
        """This is a static class, not meant to be instantiated."""

        raise TypeError('ICMPBaseType may not be instantiated')


class Types(ICMPBaseType):
    """Represents an ICMPPacket type, as combination of type and code"""
    class EchoReply(ICMPBaseType):
        type_id = 0
        ECHO_REPLY = (type_id, 0,)

    class DestinationUnreachable(ICMPBaseType):
        type_id = 3
        NETWORK_UNREACHABLE = (type_id, 0,)
        HOST_UNREACHABLE = (type_id, 1,)
        PROTOCOL_UNREACHABLE = (type_id, 2,)
        PORT_UNREACHABLE = (type_id, 3,)
        FRAGMENTATION_REQUIRED = (type_id, 4,)
        SOURCE_ROUTE_FAILED = (type_id, 5,)
        NETWORK_UNKNOWN = (type_id, 6,)
        HOST_UNKNOWN = (type_id, 7,)
        SOURCE_HOST_ISOLATED = (type_id, 8,)
        NETWORK_ADMINISTRATIVELY_PROHIBITED = (type_id, 9,)
        HOST_ADMINISTRATIVELY_PROHIBITED = (type_id, 10,)
        NETWORK_UNREACHABLE_TOS = (type_id, 11,)
        HOST_UNREACHABLE_TOS = (type_id, 12,)
        COMMUNICATION_ADMINISTRATIVELY_PROHIBITED = (type_id, 13,)
        HOST_PRECEDENCE_VIOLATION = (type_id, 14,)
        PRECEDENCE_CUTOFF = (type_id, 15,)

    class SourceQuench(ICMPBaseType):
        type_id = 4
        SOURCE_QUENCH = (type_id, 0,)

    class Redirect(ICMPBaseType):
        type_id = 5
        FOR_NETWORK = (type_id, 0,)
        FOR_HOST = (type_id, 1,)
        FOR_TOS_AND_NETWORK = (type_id, 2,)
        FOR_TOS_AND_HOST = (type_id, 3,)

    class EchoRequest(ICMPBaseType):
        type_id = 8
        ECHO_REQUEST = (type_id, 0,)

    class RouterAdvertisement(ICMPBaseType):
        type_id = 9
        ROUTER_ADVERTISEMENT = (type_id, 0,)

    class RouterSolicitation(ICMPBaseType):
        type_id = 10
        ROUTER_SOLICITATION = (type_id, 0)
        # Aliases
        ROUTER_DISCOVERY = ROUTER_SOLICITATION
        ROUTER_SELECTION = ROUTER_SOLICITATION

    class TimeExceeded(ICMPBaseType):
        type_id = 11
        TTL_EXPIRED_IN_TRANSIT = (type_id, 0)
        FRAGMENT_REASSEMBLY_TIME_EXCEEDED = (type_id, 1)

    class BadIPHeader(ICMPBaseType):
        type_id = 12
        POINTER_INDICATES_ERROR = (type_id, 0)
        MISSING_REQUIRED_OPTION = (type_id, 1)
        BAD_LENGTH = (type_id, 2)

    class Timestamp(ICMPBaseType):
        type_id = 13
        TIMESTAMP = (type_id, 0)

    class TimestampReply(ICMPBaseType):
        type_id = 14
        TIMESTAMP_REPLY = (type_id, 0)

    class InformationRequest(ICMPBaseType):
        type_id = 15
        INFORMATION_REQUEST = (type_id, 0)

    class InformationReply(ICMPBaseType):
        type_id = 16
        INFORMATION_REPLY = (type_id, 0)

    class AddressMaskRequest(ICMPBaseType):
        type_id = 17
        ADDRESS_MASK_REQUEST = (type_id, 0)

    class AddressMaskReply(ICMPBaseType):
        type_id = 18
        ADDRESS_MASK_REPLY = (type_id, 0)

    class Traceroute(ICMPBaseType):
        type_id = 30
        INFORMATION_REQUEST = (type_id, 30)


class PacketBase:
    @staticmethod
    def checksum(message):
        """Creates the ICMPPacket checksum as in RFC 1071.

        Divides the data in 16-bits chunks, then make their 1's complement sum."""

        amount = 0

        for i in range(0, len(message) - 1, 2):
            # Sum 16 bits chunks together.
            amount += ((message[i] << 8) + message[i + 1])

        # If length is odd:
        if len(message) % 2:
            # Sum the last byte plus one empty byte of padding.
            amount += (message[len(message) - 1] << 8)

        # Add carry on the right until fits in 16 bits.
        while amount >> 16:
            amount = (amount & 0xFFFF) + (amount >> 16)

        # Performs the one complement.
        check = ~amount

        # Swap bytes
        return ((check << 8) & 0xFF00) | ((check >> 8) & 0x00FF)


class ICMPPacket(PacketBase):
    def __init__(self,
                 message_type=Types.EchoReply,
                 payload=None,
                 identifier=None,
                 sequence_number=1,
                 received_checksum=None):
        """Creates an ICMPPacket packet."""

        self.message_code = 0

        if issubclass(message_type, ICMPBaseType):
            self.message_type = message_type.type_id
        elif isinstance(message_type, tuple):
            self.message_type = message_type[0]
            self.message_code = message_type[1]
        elif isinstance(message_type, int):
            self.message_type = message_type

        if payload is None:
            payload = bytes('1', 'utf8')
        elif isinstance(payload, str):
            payload = bytes(payload, 'utf8')

        self.payload = payload

        if identifier is None:
            identifier = os.getpid()

        # Prevent identifiers bigger than 16 bits.
        self.identifier = identifier & 0xFFFF
        self.sequence_number = sequence_number
        self.received_checksum = received_checksum

    def __header(self, checksum=0):
        """The raw ICMPPacket header.

        Set type, code, and version for the packet.

        Header is type (8), code (8), checksum (16), identifier (16), sequence (16)."""

        # header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, identifier, 1)
        return struct.pack(ICMPData.ICMP_STRUCTURE_FMT.value,
                           self.message_type,
                           self.message_code,
                           checksum,
                           self.identifier,
                           self.sequence_number)

    def unpack(self, raw):
        """Unpacks a raw packet and stores it in this object."""

        self.message_type, \
            self.message_code, \
            self.received_checksum, \
            self.identifier, \
            sequence = struct.unpack(ICMPData.ICMP_STRUCTURE_FMT.value, raw[20:28])

        self.payload = raw[28:]

    @property
    def packet(self):
        """The raw packet with header, ready to be sent from a socket"""

        return self.__header(checksum=self.expected_checksum) + self.payload

    @property
    def is_valid(self):
        """True if the received checksum is valid, otherwise False."""

        if self.received_checksum is None:
            return True
        return self.expected_checksum == self.received_checksum

    @property
    def expected_checksum(self):
        """The checksum expected for this packet, calculated with checksum field set to 0."""

        return self.checksum(self.__header() + self.payload)

    @property
    def header_length(self):
        """Length of the ICMPPacket header."""

        return len(self.__header())

    @staticmethod
    def generate_from_raw(raw):
        """Creates a new ICMPPacket representation from the raw bytes."""

        packet = ICMPPacket()
        packet.unpack(raw)

        return packet
