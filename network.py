#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: network.py
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

"""This module provides access to the BSD socket interface."""

import select
import socket
import time


class SocketInterface:
    """Implement of the BSD socket interface."""

    def __init__(self, destination, protocol, socket_options=(), buffer_size=2048):
        """Creates a network socket to exchange messages."""

        self.__socket = None

        try:
            self.__destination = socket.gethostbyname(destination)
        except socket.gaierror as error:
            raise RuntimeError(f'Cannot resolve the address {destination}, try verify your DNS or host file.\n{error}')

        self.__protocol = socket.getprotobyname(protocol)
        self.__buffer_size = buffer_size

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, self.protocol)

        if socket_options:
            self.socket.setsockopt(*socket_options)

    def __enter__(self):
        """Return this object."""

        return self

    def __exit__(self, *args):
        """Call the `close_socket` method."""

        self.close_socket()

    def __del__(self):
        self.close_socket()

    def close_socket(self):
        """Safe socket cleanup after all references to the object have been deleted."""

        try:
            if hasattr(self, 'socket') and not self.is_closed:
                self.socket.close()
                self.socket = None
        except AttributeError:
            raise AttributeError('Attribute error because of failed socket init. Make sure you have the root '
                                 'privilege. This error may also be caused from DNS resolution problems.')

    @property
    def is_closed(self):
        """Indicate whether the socket is closed."""

        return self.socket is None

    @property
    def destination(self):
        return self.__destination

    @property
    def buffer_size(self):
        return self.__buffer_size

    @property
    def protocol(self):

        return self.__protocol

    @property
    def socket(self):
        """Return the socket object."""

        return self.__socket

    @socket.setter
    def socket(self, value):
        """Set the socket object."""

        self.__socket = value

    @property
    def is_closed(self):
        """Indicate whether the socket is closed."""

        return self.socket is None

    def send_packet(self, packet):
        """Sends a raw packet on the stream."""

        self.socket.sendto(packet, (self.destination, 0))

    def receive_packet(self, timeout=2):
        """Listen for incoming packets until timeout."""

        time_left = timeout
        while time_left > 0:
            start_time = time.perf_counter()

            data_ready = select.select([self.socket], [], [], time_left)

            time_elapse_in_select = time.perf_counter() - start_time
            time_left -= time_elapse_in_select

            if not data_ready[0]:
                return b'', '', time_left

            packet_received, address = self.socket.recvfrom(self.buffer_size)

            return packet_received, address, time_left

    @property
    def dont_fragment(self):
        """Specifies whether sockets cannot be fragmented.

        Datagrams require fragmentation when their size exceeds the Maximum Transfer Unit (MTU) of the transmission
        medium. Datagrams may be fragmented by the sending host (all Internet Protocol versions) or an intermediate
        router (Internet Protocol Version 4 only). If a datagram must be fragmented, and the DontFragment option is
        set, the datagram is discarded, and an Internet Control Message Protocol (ICMP) error message is sent back to
        the sender of the datagram."""

        return socket.SOL_IP, 10, 1


sk = SocketInterface('google.com', 'icmp')
sk.send_packet(b'!2B3H')
received, address, time_left = sk.receive_packet()
print(sk.destination)
print(received)
print(address)
print(time_left)
