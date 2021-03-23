#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: commands.py
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

import sys

from random import randint

import provider

import executor
import network

from utils import SeedIds
from utils import random_text


class PingCommand:
    """Ping uses the ICMP protocol's mandatory ECHO_REQUEST datagram to elicit an
    ICMP ECHO_RESPONSE from a host or gateway."""

    def __init__(self,
                 destination,
                 timeout=2,
                 count=5,
                 size=1,
                 payload=None,
                 sweep_start=None,
                 sweep_end=None,
                 dont_fragment=False,
                 verbose=False,
                 output=sys.stdout,
                 match=False):
        """Send ICMP ECHO_REQUEST to network hosts."""

        # The remote hostname or IP address to ping.
        self.destination = destination

        # Time in seconds before considering each non-arrived reply permanently lost.
        self.timeout = timeout

        # How many times to attempt the ping.
        self.count = count

        # Size of the entire packet to send.
        self.size = size

        # Payload content of packet message.
        self.payload = payload

        self.sweep_start = sweep_start
        self.sweep_end = sweep_end
        self.dont_fragment = dont_fragment

        # Print output while performing operations.
        self.verbose = verbose

        # Stream to which redirect the verbose output.
        self.output = output

        self.match = match

        # List of identifiers for each thread.
        self.seed_identifiers = SeedIds()

        # Default value for socket options.
        self.options = []

    def run(self):
        """Pings a remote host and handles the responses."""

        payload_provider = provider.Repeat(b'', 0)

        if self.sweep_start and self.sweep_end and self.sweep_end >= self.sweep_start:
            if not self.payload:
                self.payload = random_text(self.sweep_start)
            payload_provider = provider.Sweep(self.payload, self.sweep_start, self.sweep_end)
        elif self.size and self.size > 0:
            if not self.payload:
                self.payload = random_text(self.size)
            payload_provider = provider.Repeat(self.payload, self.count)

        # Set the Don't Fragment bit.
        if self.dont_fragment:
            self.options = network.SocketInterface.dont_fragment

        while True:
            seed_id = randint(0x1, 0xFFFF)
            if seed_id not in self.seed_identifiers.ids:
                self.seed_identifiers.ids.append(seed_id)
                break

        communicator = executor.Communicator(self.destination,
                                             payload_provider,
                                             self.timeout,
                                             socket_options=self.options,
                                             verbose=self.verbose,
                                             output=self.output,
                                             seed_id=seed_id)

        communicator.run(match_payloads=self.match)

        self.seed_identifiers.ids.remove(seed_id)

        return communicator.responses
