#  #!/usr/bin/env python
#  encoding: utf-8
#
#  --------------------------------------------------------------------------------------------------------------------
#
#  Name: executor.py
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

"""Components for sending messages and handling responses."""
import os
import sys

from models import ICMPPacket
from models import Types

from network import SocketInterface

from utils import SuccessRequest
from utils import represent_seconds_in_milliseconds


class Message:
    """Represents an ICMPPacket message with destination socket."""

    def __init__(self, destination, packet, source):
        """Creates a message that may be sent, or used to represent a response."""

        self.__destination = destination
        self.__packet = packet
        self.__source = source

    @property
    def destination(self):
        return self.__destination

    @property
    def packet(self):
        return self.__packet

    @property
    def source(self):
        return self.__source

    def send(self, source_socket):
        """Places the message on a socket."""

        source_socket.send_packet(self.packet.packet)


class Response:
    """Represents a response to an ICMPPacket message, with metadata like timing."""

    def __init__(self, message, time_elapsed):
        """Creates a representation of ICMPPacket message received in response."""

        self.__message = message
        self.__time_elapsed = time_elapsed

    def __repr__(self):
        """Return repr(self)."""

        if self.message is None:
            return 'Request timed out.'
        elif self.success:
            return f'Reply from {self.message.source} ' \
                   f'bytes={len(self.message.packet.packet)} ' \
                   f'time={self.time_elapsed_ms}ms'
        else:
            return f'{self.error_message} from {self.message.source} in {self.time_elapsed_ms}ms'

    @property
    def message(self):
        return self.__message

    @property
    def time_elapsed(self):
        return self.__time_elapsed

    @property
    def success(self):
        return self.error_message is None

    @property
    def time_elapsed_ms(self):
        return represent_seconds_in_milliseconds(self.time_elapsed)

    @property
    def error_message(self):
        if self.message is None:
            return 'No response'
        else:
            if self.message.packet.message_type == 0 and self.message.packet.message_code == 0:
                # Echo Reply, response OK - no error
                return None
            elif self.message.packet.message_type == 3:
                # Destination unreachable, returning more details based on __message code
                unreachable_messages = [
                    'Network Unreachable',
                    'Host Unreachable',
                    'Protocol Unreachable',
                    'Port Unreachable',
                    'Fragmentation Required',
                    'Source Route Failed',
                    'Network Unknown',
                    'Host Unknown',
                    'Source Host Isolated',
                    'Communication with Destination Network is Administratively Prohibited',
                    'Communication with Destination Host is Administratively Prohibited',
                    'Network Unreachable for ToS',
                    'Host Unreachable for ToS',
                    'Communication Administratively Prohibited',
                    'Host Precedence Violation',
                    'Precedence Cutoff in Effect'
                ]

                try:
                    return unreachable_messages[self.message.packet.message_code]
                except IndexError:
                    # Should never generate IndexError, this serves as additional protection
                    return 'Unreachable'

        # Error was not identified
        return 'Network Error'


class ResponseList:
    """Represents a series of ICMPPacket responses."""

    def __init__(self, initial_set=None, verbose=False, output=sys.stdout):
        """Creates a ResponseList with initial data if available."""

        if initial_set is None:
            initial_set = []

        self.__responses = []
        self.clear_responses()
        self.verbose = verbose
        self.output = output

        # Round Trip Time
        self.__rtt_avg = 0
        self.__rtt_min = 0
        self.__rtt_max = 0
        self.__packets_lost = 0

        for response in initial_set:
            self.append(response)

    def __len__(self):
        """Return len(self)."""

        return len(self.__responses)

    def success(self, option=SuccessRequest.one):
        """Check success state of the request."""

        result = False
        success_list = [response.success for response in self.__responses]

        if option == SuccessRequest.one:
            result = True in success_list
        elif option == SuccessRequest.most:
            result = success_list.count(True) / len(success_list) > .5
        elif option == SuccessRequest.all:
            result = False not in success_list

        return result

    def clear_responses(self):
        """Clears stored responses."""
        self.__responses = []

    def append(self, response):
        """Adds value to stored responses."""

        self.__responses.append(response)

        if len(self) == 1:
            self.__rtt_avg = response.time_elapsed
            self.__rtt_max = response.time_elapsed
            self.__rtt_min = response.time_elapsed
        else:
            # Calculate the total of time, add the new value and divide for the new number
            self.__rtt_avg = ((self.__rtt_avg * (len(self) - 1)) + response.time_elapsed) / len(self)
            if response.time_elapsed > self.__rtt_max:
                self.__rtt_max = response.time_elapsed
            if response.time_elapsed < self.__rtt_min:
                self.__rtt_min = response.time_elapsed

        self.__packets_lost = self.__packets_lost + (0 if response.success else 1 - self.__packets_lost) / len(self)

        if self.verbose:
            print(response, file=self.output)

    @property
    def packets_lost(self):
        return self.__packets_lost

    @property
    def rtt_min_ms(self):
        """Smallest Round Trip Time."""

        return represent_seconds_in_milliseconds(self.__rtt_min)

    @property
    def rtt_max_ms(self):
        """Highest Round Trip Time."""

        return represent_seconds_in_milliseconds(self.__rtt_max)

    @property
    def rtt_avg_ms(self):
        """Average Round Trip Time."""

        return represent_seconds_in_milliseconds(self.__rtt_avg)


class Communicator:
    """Instance actually communicating over the network, sending messages and handling responses."""

    def __init__(self,
                 target,
                 payload_provider,
                 timeout,
                 socket_options=(),
                 seed_id=None,
                 verbose=False,
                 output=sys.stdout):
        """Creates an instance that can handle communication with the target_address device."""

        self.socket = SocketInterface(target, 'icmp', socket_options=socket_options)
        self.provider = payload_provider
        self.timeout = timeout
        self.responses = ResponseList(verbose=verbose, output=output)

        # The seed ID must be unique per thread.
        self.seed_id = seed_id
        if self.seed_id is None:
            self.seed_id = os.getpid() & 0xFFFF

    def send_ping(self, packet_id, sequence_number, payload):
        """Sends one ICMPPacket Echo Request on the socket."""

        icmp_packet = ICMPPacket(Types.EchoRequest,
                                 payload=payload,
                                 identifier=packet_id,
                                 sequence_number=sequence_number)
        self.socket.send_packet(icmp_packet.packet)

        return icmp_packet.payload

    def listen_for(self, packet_id, timeout, payload_pattern=None):
        """Listens for a packet of a given identifier for a given timeout."""

        time_left = timeout
        response = ICMPPacket()
        while time_left > 0:
            raw_received, address, time_left = self.socket.receive_packet(time_left)

            if raw_received != b'':
                response.unpack(raw_received)

                if response.identifier == packet_id and response.message_type != Types.EchoRequest.type_id:
                    if payload_pattern is None:
                        payload_matched = True
                    else:
                        payload_matched = (payload_pattern == response.payload)

                    if payload_matched:
                        return Response(Message('', response, address[0]), (timeout - time_left))

        return Response(None, timeout)

    def run(self, match_payloads=False):
        """Performs all the pings and stores the responses."""

        self.responses.clear_responses()

        identifier = self.seed_id
        sequence = 1
        for payload in self.provider:
            payload_bytes_sent = self.send_ping(identifier, sequence, payload)

            if not match_payloads:
                self.responses.append(self.listen_for(identifier, self.timeout))
            else:
                self.responses.append(self.listen_for(identifier, self.timeout, payload_bytes_sent))

            sequence = self.increase_seq(sequence)

    @staticmethod
    def increase_seq(sequence_number):
        """Increases an ICMPPacket sequence number and reset if it gets bigger than 2 bytes."""

        sequence_number += 1
        if sequence_number > 0xFFFF:
            sequence_number = 1

        return sequence_number
